# Title     :  R function for VisualNMA
# Objective :  compute NMA output via netmeta
# Created by:  Silvia Metelli
# Created on: 16/11/2020



options(warn=-1)
suppressMessages(library(dplyr))
suppressMessages(library(tidyverse))

suppressMessages(library(meta))
suppressMessages(library(metafor))

suppressMessages(library(netmeta))



iswhole <- function(x, tol = .Machine$double.eps^0.5) abs(x - round(x)) < tol

#--------------------------------------- NMA forest plots -------------------------------------------------#
run_NetMeta <- function(dat){
  ALL_DFs <- list()
  sm <- dat$effect_size1[1]
  dat <- dat %>% filter_at(vars(TE,seTE),all_vars(!is.na(.))) %>% filter(seTE!=0)
  treatments <- unique(c(dat$treat1, dat$treat2))
  # if incorrect number of arms, then delete entire study
  tabnarms <- table(dat$studlab)
  sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
  if (sum(sel.narms) >= 1){dat <- dat %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
  nma_temp <- netmeta(dat$TE, dat$seTE, dat$treat1, dat$treat2, dat$studlab,
                        sm = sm,
                        random = TRUE,
                        backtransf = TRUE,
                        #prediction = TRUE,
                        reference.group = treatments[1])
    ### Values
  for (treatment in treatments){
      treatment_list <- nma_temp$trts[nma_temp$trts != treatment]
      TE <-  nma_temp$TE.random[, treatment]
      TE_names <- names(TE)[sapply(TE, is.numeric)]
      TE <- TE[which(TE_names != treatment)]
      se <- nma_temp$seTE.random[, treatment]
      se <- se[which(TE_names != treatment)]
      ci_lo <- TE - 1.96*se
      ci_up <- TE + 1.96*se
      TEweights <- 1 / nma_temp$seTE.random[, treatment] # Precision
      TEweights <- TEweights[which(TE_names != treatment)]
      tau2 <- nma_temp$tau^2
      if(sm=="MD" | sm=="SMD"){df <- data.frame(treatment_list, TE,  ci_lo, ci_up, TEweights, tau2)
      }else{df <- data.frame(treatment_list, exp(TE),  exp(ci_lo),  exp(ci_up), TEweights, tau2)}
      colnames(df) <- c("Treatment", sm, "CI_lower", "CI_upper", "WEIGHT", "tau2")
      df['Reference'] <- treatment
      ALL_DFs[[treatment]] <- df
      #rm(nma_temp, TE, TE_names, se, ci_lo, ci_up, TEweights, tau2)
  }
  ALL_DFs <- do.call('rbind', ALL_DFs)
  return(ALL_DFs)
}

run_NetMeta_new <- function(dat, i){
  ALL_DFs <- list()
  sm <- dat[[paste0("effect_size", i+1)]][1] 

  TE_col <- paste0("TE", i+1)  
  seTE_col <- paste0("seTE", i+1)  

  # Filter rows with valid TE and non-zero SE
  dat <- dat %>%
    filter_at(vars(!!as.name(TE_col), !!as.name(seTE_col)), all_vars(!is.na(.))) %>%
    filter(!!as.name(seTE_col) != 0)

  treatments <- unique(c(dat$treat1, dat$treat2))

  # Remove studies with incorrect number of arms
  tabnarms <- table(dat$studlab)
  sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
  if(sum(sel.narms) >= 1){ dat <- dat %>% filter(!studlab %in% names(tabnarms)[sel.narms]) }

  # Run network meta-analysis
  nma_temp <- netmeta(
    TE = dat[[TE_col]], seTE = dat[[seTE_col]], treat1 = dat$treat1, treat2 = dat$treat2, studlab = dat$studlab,
    sm = sm, random = TRUE, backtransf = TRUE, reference.group = treatments[1]
  )

  # Loop over treatments to extract all values
  for (treatment in treatments){
    treatment_list <- nma_temp$trts[nma_temp$trts != treatment]

    TE <- nma_temp$TE.random[, treatment]
    TE_names <- names(TE)[sapply(TE, is.numeric)]
    TE <- TE[which(TE_names != treatment)]

    se <- nma_temp$seTE.random[, treatment]
    se <- se[which(TE_names != treatment)]

    ci_lo <- TE - 1.96 * se
    ci_up <- TE + 1.96 * se

    TEweights <- 1 / nma_temp$seTE.random[, treatment]
    TEweights <- TEweights[which(TE_names != treatment)]

    tau2 <- nma_temp$tau^2

    pre_lo <- nma_temp$lower.predict[, treatment]
    pre_up <- nma_temp$upper.predict[, treatment]
    pre_lo <- pre_lo[which(TE_names != treatment)]
    pre_up <- pre_up[which(TE_names != treatment)]

    # Direct and indirect values
    direct <- -nma_temp$TE.direct.random[treatment, treatment_list]
    direct_up <- -nma_temp$lower.direct.random[treatment, treatment_list]
    direct_lo <- -nma_temp$upper.direct.random[treatment, treatment_list]

    indirect <- -nma_temp$TE.indirect.random[treatment, treatment_list]
    indirect_up <- -nma_temp$lower.indirect.random[treatment, treatment_list]
    indirect_lo <- -nma_temp$upper.indirect.random[treatment, treatment_list]

   

    # Exponentiate if needed
    if(!(sm %in% c("MD", "SMD"))){
      TE <- exp(TE)
      ci_lo <- exp(ci_lo)
      ci_up <- exp(ci_up)
      pre_lo <- exp(pre_lo)
      pre_up <- exp(pre_up)

      direct <- exp(direct)
      direct_lo <- exp(direct_lo)
      direct_up <- exp(direct_up)

      indirect <- exp(indirect)
      indirect_lo <- exp(indirect_lo)
      indirect_up <- exp(indirect_up)
    }

    # Create DataFrame with dynamic main effect column name
    df <- data.frame(
      Treatment = treatment_list,
      stringsAsFactors = FALSE
    )

    # Add main effect column with dynamic name
    df[[sm]] <- TE
    df$CI_lower <- ci_lo
    df$CI_upper <- ci_up
    df$pre_lower <- pre_lo
    df$pre_upper <- pre_up
    df$WEIGHT <- TEweights
    df$tau2 <- tau2
    df$direct <- direct
    df$direct_lower <- direct_lo
    df$direct_upper <- direct_up
    df$indirect <- indirect
    df$indirect_lower <- indirect_lo
    df$indirect_upper <- indirect_up
    df['Reference'] <- treatment

    ALL_DFs[[treatment]] <- df
  }

  ALL_DFs <- do.call('rbind', ALL_DFs)
  return(ALL_DFs)
}



# run_NetMeta_new <- function(dat, i){
#   ALL_DFs <- list()
#   sm <- dat[[paste0("effect_size", i+1)]][1] 

#   TE_col <- paste0("TE", i+1)  # Generating the column name dynamically
#   seTE_col <- paste0("seTE", i+1)  
  
#   # Filtering and updating 'dat' using the dynamically generated column names
#   dat <- dat %>%
#     filter_at(vars(!!as.name(TE_col), !!as.name(seTE_col)), all_vars(!is.na(.))) %>%
#     filter(!!as.name(seTE_col) != 0)
  

#   treatments <- unique(c(dat$treat1, dat$treat2))
#   # if incorrect number of arms, then delete entire study
#   tabnarms <- table(dat$studlab)
#   sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
#   if (sum(sel.narms) >= 1){dat <- dat %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
#   nma_temp <- netmeta(dat[[paste0("TE", i+1)]], dat[[paste0("seTE", i+1)]], dat$treat1, dat$treat2, dat$studlab,
#                         sm = sm,
#                         random = TRUE,
#                         backtransf = TRUE,
#                         #prediction = TRUE,
#                         reference.group = treatments[1])
#     ### Values
#   for (treatment in treatments){
#       treatment_list <- nma_temp$trts[nma_temp$trts != treatment]
#       TE <-  nma_temp$TE.random[, treatment]
#       TE_names <- names(TE)[sapply(TE, is.numeric)]
#       TE <- TE[which(TE_names != treatment)]
#       se <- nma_temp$seTE.random[, treatment]
#       se <- se[which(TE_names != treatment)]
#       ci_lo <- TE - 1.96*se
#       ci_up <- TE + 1.96*se
#       TEweights <- 1 / nma_temp$seTE.random[, treatment] # Precision
#       TEweights <- TEweights[which(TE_names != treatment)]
#       tau2 <- nma_temp$tau^2
#       pre_lo <- nma_temp$lower.predict[, treatment]
#       pre_up <- nma_temp$upper.predict[, treatment]
#       pre_lo <- pre_lo[which(TE_names != treatment)]
#       pre_up <- pre_up[which(TE_names != treatment)]   

#       if(sm=="MD" | sm=="SMD"){df <- data.frame(treatment_list, TE,  ci_lo, ci_up,pre_lo, pre_up, TEweights, tau2)
#       }else{df <- data.frame(treatment_list, exp(TE),  exp(ci_lo),  exp(ci_up),exp(pre_lo), exp(pre_up), TEweights, tau2)}
#       colnames(df) <- c("Treatment", sm, "CI_lower", "CI_upper","pre_lower", "pre_upper", "WEIGHT", "tau2")
#       df['Reference'] <- treatment
#       ALL_DFs[[treatment]] <- df
#       #rm(nma_temp, TE, TE_names, se, ci_lo, ci_up, TEweights, tau2)
#   }
#   ALL_DFs <- do.call('rbind', ALL_DFs)
#   return(ALL_DFs)
# }




#--------------------------------------- NMA league table & ranking -------------------------------------------------#
## league tables for either one or two outcomes
league_rank <- function(dat, outcome2=FALSE){
  dat1 <- dat[, c("studlab", "treat1", "treat2", "TE", "seTE")]
  dat1 <- dat1 %>% filter_at(vars(TE,seTE),all_vars(!is.na(.))) %>% filter(seTE!=0)
  tabnarms <- table(dat1$studlab)
  sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
  if (sum(sel.narms) >= 1){dat1 <- dat1 %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
  sm1 <- dat$effect_size1[1]
  nma_primary <- netmeta(TE=dat1$TE, seTE=dat1$seTE,
                         treat1=dat1$treat1, treat2=dat1$treat2,
                         studlab=dat1$studlab,
                         sm =sm1,
                         random=TRUE, backtransf=TRUE,
                         reference.group=dat1$treat2[1])
  sortedseq <- sort(nma_primary$trts)
  netleague_table <- netleague(nma_primary, digits = 2,
                               seq=sortedseq,
                               bracket="(",
                               backtransf=TRUE, ci=TRUE, separator=',')
  lt <- netleague_table$random
  colnames(lt) <- sortedseq
  rownames(lt) <- sortedseq
  #p-scores
  rank1 <- netrank(nma_primary, small.values = "bad")
  rank <- data.frame(names(rank1$Pscore.random), as.numeric(round(rank1$Pscore.random,2)))
  colnames(rank)  <-  c("treatment", "pscore")
  #consistency
  consistency <- data.frame(nma_primary$Q.inconsistency, nma_primary$df.Q.inconsistency, nma_primary$pval.Q.inconsistency)
  colnames(consistency)  <-  c("Q", "df(Q)", "p-value")
  #consistency node-split
  ne <- netsplit(nma_primary)
  comparison <- ne$compare.random$comparison[!is.na(ne$compare.random$p)]
  direct <- exp(ne$direct.random$TE[!is.na(ne$compare.random$p)])
  indirect <- exp(ne$indirect.random$TE[!is.na(ne$compare.random$p)])
  p <- ne$compare.random$p[!is.na(ne$compare.random$p)]
  df_cons <- data.frame(comparison, direct, indirect, p)
  colnames(df_cons) <- c("comparison", "direct", "indirect", "p-value")
  comp_all <- ne$compare.random$comparison
  k_all <- ne$k
  direct_all <- exp(ne$direct.random$TE)
  nma_all <- exp(ne$random$TE)
  indirect_all <- exp(ne$indirect.random$TE)
  p_all <- ne$compare.random$p
  netsplit_all <- data.frame(comp_all, k_all, direct_all, nma_all, indirect_all, p_all)
  colnames(netsplit_all) <- c("comparison", "k", "direct", "nma", "indirect", "p-value")
  if (all(is.na(ne$compare.random$p)) == TRUE){
      df_cons <- data.frame(comp_all, direct_all, indirect_all, p_all)
      colnames(df_cons) <- c("comparison", "direct", "indirect", "p-value")
    }
  if(outcome2==TRUE){
    dat2 <- dat[, c("studlab", "treat1", "treat2", "TE2", "seTE2")]
    dat2 <- dat2 %>% filter_at(vars(TE2,seTE2),all_vars(!is.na(.))) %>% filter(seTE2!=0)
    tabnarms <- table(dat2$studlab)
    sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
    if (sum(sel.narms) >= 1){dat2 <- dat2 %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
    sm2 <- dat$effect_size2[1]
    nma_secondary <- netmeta(TE=dat2$TE2, seTE=dat2$seTE2,
                             treat1=dat2$treat1, treat2=dat2$treat2,
                             studlab=dat2$studlab, sm=sm2,
                             random=TRUE, backtransf=TRUE,
                             reference.group=dat2$treat2[1])

    # - network estimates of first outcome in lower triangle, second outcome in upper triangle
    #if(length(sort(nma_primary$trts))>length(sort(nma_secondary$trts))){sortedseq <- sort(nma_primary$trts)}else{sortedseq <- sort(nma_secondary$trts)}

    netleague_table1 <- netleague(nma_primary, digits=2,
                             bracket="(",  direct=FALSE,
                             backtransf=TRUE, ci=TRUE, separator=',')
    netleague_table2 <- netleague(nma_secondary, digits=2,
                             bracket="(", direct=FALSE,
                             backtransf=TRUE, ci=TRUE, separator=',')

    lt1 <- netleague_table1$random
    lt2 <- netleague_table2$random
    l1_treats <- sort(nma_primary$trts)
    l2_treats <- sort(nma_secondary$trts)
    lt1[upper.tri(lt1)] <- NA
    lt2[upper.tri(lt2)] <- NA
    df_1 <-  as_tibble(lt1)
    df_2 <-  as_tibble(t(lt2))

    if(length(lt1)>length(lt2)){
      which_trts <- which(!(l1_treats %in% l2_treats))
      df_2 <- df_2 %>% add_column(NA,  .before = colnames(df_2)[which_trts], .name_repair = "universal")
      colnames <- paste0("V", 1:dim(df_2)[1])
      colnames(df_2) <- colnames
      df_2 <- df_2 %>% add_row( .before = as.numeric(rownames(df_2)[which_trts] ))
      for(x in which_trts){
        df_2[x, colnames[which_trts]] <- l1_treats[x]}
      lt <- matrix(NA, nrow = length(df_1), ncol = length(df_1))
      lt[upper.tri(lt, diag=T)] <- df_2[upper.tri(df_2, diag=T)]
      lt[lower.tri(lt, diag=T)] <- df_1[lower.tri(df_1, diag=T)]
      lt <- data.frame(lt)
      sortedseq <- l1_treats
    }else if (length(lt1)==length(lt2)){
      l1_treats <- sort(nma_primary$trts)
      df_1 <-  as_tibble(lt1)
      df_2 <-  as_tibble(t(lt2))
      lt <- matrix(NA, nrow = length(df_1), ncol = length(df_1))
      lt[upper.tri(lt, diag=T)] <- df_2[upper.tri(df_2, diag=T)]
      lt[lower.tri(lt, diag=T)] <- df_1[lower.tri(df_1, diag=T)]
      lt <- data.frame(lt)
      sortedseq <- l1_treats
    }else{
     is.empty <- function(x, mode = NULL){
        if (is.null(mode)) mode <- class(x)
        identical(vector(mode, 1), c(x, vector(class(x), 1)))}
        which_trts <- which(!(l2_treats %in% l1_treats))
      if(!is.empty(which_trts,"integer")){
        df_1 <- df_1 %>% add_column(NA,  .before = colnames(df_1)[which_trts], .name_repair = "universal")
        colnames <- paste0("V", 1:dim(df_1)[1])
        colnames(df_1) <- colnames
        df_1 <- df_1 %>% add_row( .before = as.numeric(rownames(df_1)[which_trts] ))
        for(x in which_trts){
          df_1[x, colnames[which_trts]] <- l2_treats[x]}
      }
      lt <- matrix(NA, nrow = length(df_2), ncol = length(df_2))
      lt[upper.tri(lt, diag=T)] <- df_2[upper.tri(df_2, diag=T)]
      lt[lower.tri(lt, diag=T)] <- df_1[lower.tri(df_1, diag=T)]
      lt <- data.frame(lt)
      sortedseq <- l2_treats

    }
    colnames(lt) <- sortedseq
    rownames(lt) <- sortedseq
    #p-scores
    # outcomes <- c("Outcome1", "Outcome2")
    rank1 <- netrank(nma_primary, small.values = "bad")
    rank2 <- netrank(nma_secondary, small.values = "bad")
    r1 <- data.frame(names(rank1$Pscore.random), round(as.numeric(rank1$Pscore.random),2))
    colnames(r1)  <-  c("treatment", "pscore")
    r2 <- data.frame(names(rank2$Pscore.random), round(as.numeric(rank2$Pscore.random),2))
    colnames(r2)  <-  c("treatment", "pscore")
    rank <- merge(r1, r2, by = "treatment", all.x = TRUE)
    colnames(rank)  <-  c("treatment", "pscore1",  "pscore2")
    #consistency design by treat
    consistency <- data.frame(rbind("Outcome1", "Outcome2"),
                              rbind(nma_primary$Q.inconsistency, nma_secondary$Q.inconsistency),
                              rbind(nma_primary$df.Q.inconsistency, nma_secondary$df.Q.inconsistency),
                              rbind(nma_primary$pval.Q.inconsistency, nma_secondary$pval.Q.inconsistency)
                              )

    colnames(consistency)  <-  c("Outcome", "Q","df(Q)", "p-value")
    #consistency node-split
    ne2 <- netsplit(nma_secondary)
    comparison2 <- ne2$compare.random$comparison[!is.na(ne2$compare.random$p)]
    direct2<- exp(ne2$direct.random$TE[!is.na(ne2$compare.random$p)])
    indirect2 <- exp(ne2$indirect.random$TE[!is.na(ne2$compare.random$p)])
    p2 <- ne2$compare.random$p[!is.na(ne2$compare.random$p)]
    df_cons2 <- data.frame(comparison2, direct2, indirect2, p2)
    colnames(df_cons2) <- c("comparison", "direct", "indirect", "p-value")
    comp_all2 <- ne2$compare.random$comparison
    k_all2 <- ne2$k
    direct_all2 <- exp(ne2$direct.random$TE)
    nma_all2 <- exp(ne2$random$TE)
    indirect_all2 <- exp(ne2$indirect.random$TE)
    p_all2 <- ne2$compare.random$p
    netsplit_all2 <- data.frame(comp_all2, k_all2, direct_all2, nma_all2, indirect_all2, p_all2)
    colnames(netsplit_all2) <- c("comparison", "k", "direct", "nma", "indirect", "p-value")
    if (all(is.na(ne2$compare.random$p))==TRUE){
      df_cons <- data.frame(comp_all2, direct_all2, indirect_all2, p_all2)
      colnames(df_cons) <- c("comparison", "direct", "indirect", "p-value")
    }
  }
  if(outcome2==TRUE){return(list(lt, rank, consistency, df_cons, df_cons2, netsplit_all, netsplit_all2))}else{
    return(list(lt, rank, consistency, df_cons, netsplit_all))
  }
}



league_rank_new <- function(dat, i){
    sm <- dat[[paste0("effect_size", i+1)]][1] 
    TE_col <- paste0("TE", i+1)  # Generating the column name dynamically
    seTE_col <- paste0("seTE", i+1)  
    dat1 <- dat[, c("studlab", "treat1", "treat2", TE_col, seTE_col)]
    # Filtering and updating 'dat' using the dynamically generated column names
    dat1 <- dat1 %>%
        filter_at(vars(!!as.name(TE_col), !!as.name(seTE_col)), all_vars(!is.na(.))) %>%
        filter(!!as.name(seTE_col) != 0)
    tabnarms <- table(dat1$studlab)
    sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
    if (sum(sel.narms) >= 1){dat1 <- dat1 %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
    sm1 <- dat[[paste0("effect_size", i+1)]][1]
    nma_primary <- netmeta(dat1[[paste0("TE", i+1)]], dat1[[paste0("seTE", i+1)]],
                         treat1=dat1$treat1, treat2=dat1$treat2,
                         studlab=dat1$studlab,
                         sm =sm1,
                         random=TRUE, backtransf=TRUE,
                         reference.group=dat1$treat2[1])
    sortedseq <- sort(nma_primary$trts)
    netleague_table <- netleague(nma_primary, digits = 2,
                                seq=sortedseq,
                                bracket="(",
                                backtransf=TRUE, ci=TRUE, separator=',')
    lt <- netleague_table$random
    colnames(lt) <- sortedseq
    rownames(lt) <- sortedseq
    #p-scores
    rank1 <- netrank(nma_primary, small.values = "bad")
    rank <- data.frame(names(rank1$Pscore.random), as.numeric(round(rank1$Pscore.random,2)))
    colnames(rank)  <-  c("treatment", "pscore")
    #consistency
    consistency <- data.frame(nma_primary$Q.inconsistency, nma_primary$df.Q.inconsistency, nma_primary$pval.Q.inconsistency)
    colnames(consistency)  <-  c("Q", "df(Q)", "p-value")
    #consistency node-split
    ne <- netsplit(nma_primary)
    comparison <- ne$compare.random$comparison[!is.na(ne$compare.random$p)]
    
    if (sm == "OR" || sm == "RR") {
        direct <- exp(ne$direct.random$TE[!is.na(ne$compare.random$p)])
        di_lower <- exp(ne$direct.random$lower[!is.na(ne$compare.random$p)])
        di_upper <- exp(ne$direct.random$upper[!is.na(ne$compare.random$p)])
        indirect <- exp(ne$indirect.random$TE[!is.na(ne$compare.random$p)])
        indi_lower <- exp(ne$indirect.random$lower[!is.na(ne$compare.random$p)])
        indi_upper <- exp(ne$indirect.random$upper[!is.na(ne$compare.random$p)])
    } else {
        direct <- ne$direct.random$TE[!is.na(ne$compare.random$p)]
        di_lower <- ne$direct.random$lower[!is.na(ne$compare.random$p)]
        di_upper <- ne$direct.random$upper[!is.na(ne$compare.random$p)]
        indirect <- ne$indirect.random$TE[!is.na(ne$compare.random$p)]
        indi_lower <- ne$indirect.random$lower[!is.na(ne$compare.random$p)]
        indi_upper <- ne$indirect.random$upper[!is.na(ne$compare.random$p)]
    }
    
    p <- ne$compare.random$p[!is.na(ne$compare.random$p)]
    direct <- ifelse(
                  length(direct) > 0 & !is.na(direct),
                  paste0(round(direct, 2), " (", round(di_lower, 2), ", ", round(di_upper, 2), ")"),
                  direct
                )

    indirect <- ifelse(
      length(indirect) > 0 & !is.na(indirect),
      paste0(round(indirect, 2), " (", round(indi_lower, 2), ", ", round(indi_upper, 2), ")"),
      indirect
    )
    df_cons <- data.frame(comparison, direct, indirect, p)
    colnames(df_cons) <- c("comparison", "direct", "indirect", "p-value")
    comp_all <- ne$compare.random$comparison
    k_all <- ne$k
    
    if (sm == "OR" || sm == "RR") {
        direct_all <- exp(ne$direct.random$TE)
        direct_low <- exp(ne$direct.random$lower)
        direct_up  <- exp(ne$direct.random$upper)
        nma_all <- exp(ne$random$TE)
        indirect_all <- exp(ne$indirect.random$TE)
        indirect_low <- exp(ne$indirect.random$lower)
        indirect_up  <- exp(ne$indirect.random$upper)
    } else {
        direct_all <- ne$direct.random$TE
        direct_low <- ne$direct.random$lower
        direct_up  <- ne$direct.random$upper
        nma_all <- ne$random$TE
        indirect_all <- ne$indirect.random$TE
        indirect_low <- ne$indirect.random$lower
        indirect_up  <- ne$indirect.random$upper
    }
    
    p_all <- ne$compare.random$p
    netsplit_all <- data.frame(comp_all, k_all, direct_all,direct_low, direct_up, nma_all, indirect_all, indirect_low, indirect_up, p_all)
    colnames(netsplit_all) <- c("comparison", "k", "direct", 'direct_low', 'direct_up', "nma", "indirect",'indirect_low', 'indirect_up', "p-value")
    if (all(is.na(ne$compare.random$p)) == TRUE){
        df_cons <- data.frame(comp_all, direct_all, indirect_all, p_all)
        colnames(df_cons) <- c("comparison", "direct", "indirect", "p-value")
        }
  
    return(list(lt, rank, consistency, df_cons, netsplit_all))
}



league_both <- function(dat, i, j){
    # ---- Outcome i (primary) ----
    sm1 <- dat[[paste0("effect_size", i+1)]][1] 
    TE_col <- paste0("TE", i+1)
    seTE_col <- paste0("seTE", i+1)  
    dat1 <- dat[, c("studlab", "treat1", "treat2", TE_col, seTE_col)]
    dat1 <- dat1 %>%
        filter_at(vars(!!as.name(TE_col), !!as.name(seTE_col)), all_vars(!is.na(.))) %>%
        filter(!!as.name(seTE_col) != 0)
    tabnarms <- table(dat1$studlab)
    sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
    if (sum(sel.narms) >= 1){dat1 <- dat1 %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
    
    nma_primary <- netmeta(dat1[[TE_col]], dat1[[seTE_col]],
                         treat1=dat1$treat1, treat2=dat1$treat2,
                         studlab=dat1$studlab,
                         sm=sm1,
                         random=TRUE, backtransf=TRUE,
                         reference.group=dat1$treat2[1])
    
    l1_treats <- sort(nma_primary$trts)
    netleague_table1 <- netleague(nma_primary, digits=2, seq=l1_treats,
                                  bracket="(", backtransf=TRUE, ci=TRUE, separator=',')
    lt1 <- netleague_table1$random
    colnames(lt1) <- l1_treats
    rownames(lt1) <- l1_treats

    # ---- Outcome j (secondary) ----
    sm2 <- dat[[paste0("effect_size", j+1)]][1] 
    TE_col2 <- paste0("TE", j+1)
    seTE_col2 <- paste0("seTE", j+1)  
    dat2 <- dat[, c("studlab", "treat1", "treat2", TE_col2, seTE_col2)]
    dat2 <- dat2 %>%
        filter_at(vars(!!as.name(TE_col2), !!as.name(seTE_col2)), all_vars(!is.na(.))) %>%
        filter(!!as.name(seTE_col2) != 0)
    tabnarms <- table(dat2$studlab)
    sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
    if (sum(sel.narms) >= 1){dat2 <- dat2 %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
    
    nma_secondary <- netmeta(dat2[[TE_col2]], dat2[[seTE_col2]],
                        treat1=dat2$treat1, treat2=dat2$treat2,
                        studlab=dat2$studlab,
                        sm=sm2,
                        random=TRUE, backtransf=TRUE,
                        reference.group=dat2$treat2[1])
    
    l2_treats <- sort(nma_secondary$trts)
    netleague_table2 <- netleague(nma_secondary, digits=2, seq=l2_treats,
                                  bracket="(", backtransf=TRUE, ci=TRUE, separator=',')
    lt2 <- netleague_table2$random
    colnames(lt2) <- l2_treats
    rownames(lt2) <- l2_treats

    # ---- Combine: union of all treatments ----
    all_treats <- sort(unique(c(l1_treats, l2_treats)))
    n <- length(all_treats)
    
    # Create empty combined matrix
    lt <- matrix(NA_character_, nrow=n, ncol=n)
    colnames(lt) <- all_treats
    rownames(lt) <- all_treats
    
    # Fill diagonal with treatment names
    for (k in 1:n) {
        lt[k, k] <- all_treats[k]
    }
    
    # Fill lower triangle from outcome i (lt1)
    for (row_t in l1_treats) {
        for (col_t in l1_treats) {
            row_idx <- which(all_treats == row_t)
            col_idx <- which(all_treats == col_t)
            # lower triangle: row > col
            if (row_idx > col_idx) {
                lt[row_idx, col_idx] <- lt1[row_t, col_t]
            }
        }
    }
    
    # Fill upper triangle from outcome j (lt2)
    # Use lt2's lower triangle values but place them in upper triangle (transposed)
    for (row_t in l2_treats) {
        for (col_t in l2_treats) {
            row_idx <- which(all_treats == row_t)
            col_idx <- which(all_treats == col_t)
            # upper triangle: row < col
            # Get value from lt2's lower triangle (col_t, row_t) and place in upper triangle (row_idx, col_idx)
            if (row_idx < col_idx) {
                lt[row_idx, col_idx] <- lt2[col_t, row_t]
            }
        }
    }
    
    lt <- data.frame(lt, stringsAsFactors=FALSE)
    colnames(lt) <- all_treats
    rownames(lt) <- all_treats
    
    return(lt)
}





## comparison adjusted funnel plots
funnel_funct <- function(dat){
  ALL_DFs <- list()
  sm <- dat$effect_size1[1]
  dat <- dat %>% filter_at(vars(TE,seTE),all_vars(!is.na(.))) %>% filter(seTE!=0)
  iswhole <- function(x, tol = .Machine$double.eps^0.5) abs(x - round(x)) < tol
  tabnarms <- table(dat$studlab)
  sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)
  if (sum(sel.narms) >= 1){dat <- dat %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
  treatments <- unique(c(dat$treat1, dat$treat2))
  x <- netmeta(TE=dat$TE, seTE=dat$seTE,
                 treat1=dat$treat1, treat2=dat$treat2,
                 studlab=dat$studlab,
                 sm = sm,
                 random = TRUE,
                 backtransf = FALSE,
                 reference.group = treatments[1])
  for (treatment in treatments){
    ordered_strategies <- unique(c(dat$treat1, dat$treat2))
    ordered_strategies <- ordered_strategies[ordered_strategies!=treatment]
    ordered_strategies <- c(ordered_strategies, rev(treatment))
    TE <- x$TE
    seTE <- x$seTE
    treat1 <- x$treat1
    treat2 <- x$treat2
    trts.abbr <- x$trts
    trt1 <- as.character(factor(treat1, levels = x$trts, labels = trts.abbr))
    trt2 <- as.character(factor(treat2, levels = x$trts, labels = trts.abbr))
    studlab <- x$studlab
    sep.trts <- ":"
    comp <- paste(trt1, trt2, sep = sep.trts)
    comp21 <- paste(trt2, trt1, sep = sep.trts)
    comparison <- paste(treat1, treat2, sep = sep.trts)
    comparison21 <- paste(treat2, treat1, sep = sep.trts)
    treat1.pos <- as.numeric(factor(treat1, levels = ordered_strategies))
    treat2.pos <- as.numeric(factor(treat2, levels = ordered_strategies))
    wo <- treat1.pos > treat2.pos
    if (any(wo)) {
      TE[wo] <- -TE[wo]
      ttreat1 <- treat1
      treat1[wo] <- treat2[wo]
      treat2[wo] <- ttreat1[wo]
      ttreat1.pos <- treat1.pos
      treat1.pos[wo] <- treat2.pos[wo]
      treat2.pos[wo] <- ttreat1.pos[wo]
      comp[wo] <- comp21[wo]
      comparison[wo] <- comparison21[wo]
    }
    o <- order(treat1.pos, treat2.pos)
    TE <- TE[o]
    seTE <- seTE[o]
    treat1 <- treat1[o]
    treat2 <- treat2[o]
    studlab <- studlab[o]
    comp <- comp[o]
    comparison <- comparison[o]
    res <- data.frame(studlab, treat1, treat2, comparison, comp, TE, TE.direct = NA, TE.adj = NA, seTE)
    if (is.numeric(treat1)){treat1 <- as.character(treat1)}
    if (is.numeric(treat2)){treat2 <- as.character(treat2)}
    if (x$fixed == TRUE){
           for (i in seq_along(res$TE))
               res$TE.direct[i] <- x$TE.direct.fixed[treat1[i], treat2[i]]
    }else{
           for (i in seq_along(res$TE))
             res$TE.direct[i] <- x$TE.direct.random[treat1[i], treat2[i]]
    }
    res$TE.adj <- res$TE - res$TE.direct
    #netfun <- funnel(nma, order=ordered_strategies)
    funneldata <- droplevels(subset(res, treat2==treatment))
    df <- data.frame(funneldata$studlab, funneldata$treat1, funneldata$treat2, funneldata$TE,
                                  funneldata$TE.direct, funneldata$TE.adj, funneldata$seTE)
    colnames(df) <- c("studlab", "treat1", "treat2", sm, "TE_direct", "TE_adj", "seTE")
    rownames(df) <- NULL
    ALL_DFs[[treatment]] <- df

  }
  ALL_DFs <- do.call('rbind', ALL_DFs)
  return(ALL_DFs)
}



funnel_funct_new <- function(dat,i){

  ALL_DFs <- list()
  sm <- dat[[paste0("effect_size", i+1)]][1]

  TE_col <- paste0("TE", i+1)  # Generating the column name dynamically
  seTE_col <- paste0("seTE", i+1)  
  
  # Filtering and updating 'dat' using the dynamically generated column names
  dat <- dat %>%
    filter_at(vars(!!as.name(TE_col), !!as.name(seTE_col)), all_vars(!is.na(.))) %>%
    filter(!!as.name(seTE_col) != 0)

  iswhole <- function(x, tol = .Machine$double.eps^0.5) abs(x - round(x)) < tol

  tabnarms <- table(dat$studlab)
  sel.narms <- !iswhole((1 + sqrt(8 * tabnarms + 1)) / 2)

  if (sum(sel.narms) >= 1){dat <- dat %>% filter(!studlab %in% names(tabnarms)[sel.narms])}
  treatments <- unique(c(dat$treat1, dat$treat2))

  x <- netmeta(dat[[paste0("TE", i+1)]], dat[[paste0("seTE", i+1)]],
                 treat1=dat$treat1, treat2=dat$treat2,
                 studlab=dat$studlab,
                 sm = sm,
                 random = TRUE,
                 backtransf = FALSE,
                 reference.group = treatments[1])
  for (treatment in treatments){
    ordered_strategies <- unique(c(dat$treat1, dat$treat2))
    ordered_strategies <- ordered_strategies[ordered_strategies!=treatment]
    ordered_strategies <- c(ordered_strategies, rev(treatment))
    TE <- x$TE
    seTE <- x$seTE
    treat1 <- x$treat1
    treat2 <- x$treat2
    trts.abbr <- x$trts
    trt1 <- as.character(factor(treat1, levels = x$trts, labels = trts.abbr))
    trt2 <- as.character(factor(treat2, levels = x$trts, labels = trts.abbr))
    studlab <- x$studlab
    sep.trts <- ":"
    comp <- paste(trt1, trt2, sep = sep.trts)
    comp21 <- paste(trt2, trt1, sep = sep.trts)
    comparison <- paste(treat1, treat2, sep = sep.trts)
    comparison21 <- paste(treat2, treat1, sep = sep.trts)
    treat1.pos <- as.numeric(factor(treat1, levels = ordered_strategies))
    treat2.pos <- as.numeric(factor(treat2, levels = ordered_strategies))
    wo <- treat1.pos > treat2.pos
    if (any(wo)) {
      TE[wo] <- -TE[wo]
      ttreat1 <- treat1
      treat1[wo] <- treat2[wo]
      treat2[wo] <- ttreat1[wo]
      ttreat1.pos <- treat1.pos
      treat1.pos[wo] <- treat2.pos[wo]
      treat2.pos[wo] <- ttreat1.pos[wo]
      comp[wo] <- comp21[wo]
      comparison[wo] <- comparison21[wo]
    }
    o <- order(treat1.pos, treat2.pos)
    TE <- TE[o]
    seTE <- seTE[o]
    treat1 <- treat1[o]
    treat2 <- treat2[o]
    studlab <- studlab[o]
    comp <- comp[o]
    comparison <- comparison[o]
    res <- data.frame(studlab, treat1, treat2, comparison, comp, TE, TE.direct = NA, TE.adj = NA, seTE)
    if (is.numeric(treat1)){treat1 <- as.character(treat1)}
    if (is.numeric(treat2)){treat2 <- as.character(treat2)}
    if (x$fixed == TRUE){
           for (i in seq_along(res$TE))
               res$TE.direct[i] <- x$TE.direct.fixed[treat1[i], treat2[i]]
    }else{
           for (i in seq_along(res$TE))
             res$TE.direct[i] <- x$TE.direct.random[treat1[i], treat2[i]]
    }
    res$TE.adj <- res$TE - res$TE.direct
    #netfun <- funnel(nma, order=ordered_strategies)
    funneldata <- droplevels(subset(res, treat2==treatment))
    df <- data.frame(funneldata$studlab, funneldata$treat1, funneldata$treat2, funneldata$TE,
                                  funneldata$TE.direct, funneldata$TE.adj, funneldata$seTE)
    colnames(df) <- c("studlab", "treat1", "treat2", sm, "TE_direct", "TE_adj", "seTE")
    rownames(df) <- NULL
    ALL_DFs[[treatment]] <- df

  }
  ALL_DFs <- do.call('rbind', ALL_DFs)
  return(ALL_DFs)
}



#------------------------------------- pairwise forest plots -------------------------------------------#
## pairwise forest plots for all different comparisons in df
## sorted_dat: dat sorted by treatemnt comparison

pairwise_forest_new <- function(dat,i){
    DFs_pairwise <- list()
    sm <- dat[[paste0("effect_size", i+1)]][1]
    TE_col <- paste0("TE", i+1)  # Generating the column name dynamically
    seTE_col <- paste0("seTE", i+1)  
    
    # Filtering and updating 'dat' using the dynamically generated column names
    dat <- dat %>%
        filter_at(vars(!!as.name(TE_col), !!as.name(seTE_col)), all_vars(!is.na(.))) %>%
        filter(!!as.name(seTE_col) != 0)
    dat <- dat %>% arrange(dat, treat1, treat2)

    dat <- dat %>%
      mutate(
          !!as.name(TE_col) := ifelse(treat1 > treat2, -!!as.name(TE_col), !!as.name(TE_col)),
          temp = ifelse(treat1 > treat2, treat2, treat1),
          treat2 = ifelse(treat1 > treat2, treat1, treat2),
          treat1 = temp
      ) %>%
    select(-temp)

    dat$ID <- dat %>% group_indices(treat1, treat2)

    for (id in dat$ID){
    dat_temp <- dat[which(dat$ID==id), ]
    model_temp <- metagen(dat_temp[[paste0("TE", i+1)]], dat_temp[[paste0("seTE", i+1)]],
                            studlab = studlab, data=dat_temp,
                            random = T, sm=sm, prediction=TRUE)

    studlab <- dat_temp$studlab
    t1 <- dat_temp$treat1
    t2 <- dat_temp$treat2
    TE <- model_temp$TE
    TE_diamond <- model_temp$TE.random
    se <- model_temp$seTE.random
    ci_lo <- model_temp$lower.random
    ci_up <- model_temp$upper.random
    ci_lo_individual <- model_temp$lower
    ci_up_individual <- model_temp$upper
    predict_lo <- model_temp$lower.predict
    predict_up <- model_temp$upper.predict
    TEweights <- model_temp$w.random
    tau2 <- model_temp$tau^2
    I2 <- model_temp$I2
    if(sm=="MD" | sm=="SMD"){df <- data.frame(TE, TE_diamond, id, studlab, t1, t2, ci_lo_individual,
                                                ci_up_individual, ci_lo, ci_up, predict_lo, predict_up,
                                                TEweights, tau2, I2)
    }else{df <- data.frame(exp(TE), exp(TE_diamond), id, studlab, t1, t2, exp(ci_lo_individual),
                            exp(ci_up_individual), exp(ci_lo), exp(ci_up), exp(predict_lo),
                            exp(predict_up), TEweights, tau2, I2)}
    colnames(df) <- c(sm , "TE_diamond", "id", "studlab", "treat1", "treat2", "CI_lower",
                            "CI_upper", "CI_lower_diamond", "CI_upper_diamond", "Predict_lo",
                            "Predict_up", "WEIGHT", "tau2", "I2")
    DFs_pairwise[[id]] <- df
    }
  DFs_pairwise <- do.call('rbind', DFs_pairwise)
  return(DFs_pairwise)
}








#----------------------------------- pairwise function to convert long data -----------------------------------------#

get_pairwise_data_long_new <- function(dat, num_outcome=1){
   pairwise_dat <- list()
   extra_cols_list <- list()
   for (i in 1:num_outcome){
    sm <- dat[[paste0("effect_size", i)]][1] 
    if(sm %in% c('RR','OR')) {

        pair_dat <- meta::pairwise(data=dat,
                                       event=dat[[paste0("r", i)]],
                                       n=dat[[paste0("n", i)]],
                                       studlab=studlab,
                                       treat=treat,
                                       incr=0.5,
                                       sm=sm)
        pairwise_dat[[i]] <- pair_dat[,1:9]
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'TE'] <- paste0("TE", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'seTE'] <- paste0("seTE", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'event1'] <- paste0("event1", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'event2'] <- paste0("event2", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'n1'] <- paste0("n1", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'n2'] <- paste0("n2", i)
    }else {
        
        pair_dat <- meta::pairwise(data=dat,
                                            mean=dat[[paste0("y", i)]],
                                            sd=dat[[paste0("sd", i)]],
                                            n=dat[[paste0("n", i)]],
                                            studlab=studlab,
                                            treat=treat,
                                            incr=0.5,
                                            sm=sm)
        pairwise_dat[[i]] <- pair_dat[,1:9]                                   
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'TE'] <- paste0("TE", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'seTE'] <- paste0("seTE", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'event1'] <- paste0("event1", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'event2'] <- paste0("event2", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'n1'] <- paste0("n1", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'n2'] <- paste0("n2", i)
        }
      ## extract extra columns (everything after column 9) and store in a list
    add_columns <- names(pair_dat)[10:length(pair_dat)]
    extra_cols_list[[i]] <- pair_dat[, add_columns, drop = FALSE]
    }
    # pick the longest (max rows)
    new_cols <- extra_cols_list[[ which.max(sapply(extra_cols_list, nrow)) ]]
    final_dat = reduce(pairwise_dat, full_join, by = c("studlab","treat1","treat2"))
    # add_columns <- names(pair_dat)[10:length(names(pair_dat))]
    
    # new_cols <- pair_dat %>%
    # dplyr::select(add_columns)
    # combine safely
    final_dat1 <- cbind(final_dat, new_cols)
   
    # final_dat1 <- cbind.data.frame(final_dat,new_cols)

    names(final_dat1) <- c(names(final_dat),names(new_cols))

    # Rename rob1/year1 back to rob/year (meta::pairwise adds "1" suffix to extra columns)
    names(final_dat1)[names(final_dat1) == 'rob1'] <- 'rob'
    names(final_dat1)[names(final_dat1) == 'year1'] <- 'year'

    return(final_dat1)
}
#----------------------------------- pairwise function to convert contrast data -----------------------------------------#
get_pairwise_data_contrast_new <- function(dat, num_outcome=1){
   pairwise_dat <- list()
   extra_cols_list <- list()
   for (i in 1:num_outcome){
    sm <- dat[[paste0("effect_size", i)]][1]
    sm_norm <- toupper(trimws(as.character(sm)))

    colname_or_fallback <- function(primary, fallback=NULL){
      if (primary %in% names(dat)) return(primary)
      if (!is.null(fallback) && fallback %in% names(dat)) return(fallback)
      return(primary)
    }

    r1_col <- colname_or_fallback(paste0("r1", i), "r1")
    r2_col <- colname_or_fallback(paste0("r2", i), "r2")
    n1_col <- colname_or_fallback(paste0("n1", i), "n1")
    n2_col <- colname_or_fallback(paste0("n2", i), "n2")
    y1_col <- colname_or_fallback(paste0("y1", i), "y1")
    y2_col <- colname_or_fallback(paste0("y2", i), "y2")
    sd1_col <- colname_or_fallback(paste0("sd1", i), "sd1")
    sd2_col <- colname_or_fallback(paste0("sd2", i), "sd2")

    if(sm_norm %in% c('RR','OR','RD')) {
        dat_i <- dat[complete.cases(
                  dat[[r1_col]],
                  dat[[r2_col]],
                  dat[[n1_col]],
                  dat[[n2_col]],
                  dat$treat1,
                  dat$treat2,
                  dat$studlab
                ), ]

        pair_dat <- meta::pairwise(data=dat_i,
                           event=list(dat_i[[r1_col]], dat_i[[r2_col]]),
                           n=list(dat_i[[n1_col]], dat_i[[n2_col]]),
                           studlab=studlab,
                           treat=list(treat1,treat2),
                           sm=sm)

        pairwise_dat[[i]] <- pair_dat[,1:9]
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'TE'] <- paste0("TE", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'seTE'] <- paste0("seTE", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'event1'] <- paste0("event1", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'event2'] <- paste0("event2", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'n1'] <- paste0("n1", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'n2'] <- paste0("n2", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'treat_class1'] <- paste0("treat_class1", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'treat_class2'] <- paste0("treat_class2", i)
    }else {
        dat_i <- dat[complete.cases(
                  dat[[y1_col]],
                  dat[[y2_col]],
                  dat[[sd1_col]],
                  dat[[sd2_col]],
                  dat[[n1_col]],
                  dat[[n2_col]],
                  dat$studlab,
                  dat$treat1,
                  dat$treat2
                ), ]
        pair_dat <- meta::pairwise(data=dat_i,
                           mean=list(dat_i[[y1_col]], dat_i[[y2_col]]),
                           sd=list(dat_i[[sd1_col]], dat_i[[sd2_col]]),
                           n=list(dat_i[[n1_col]], dat_i[[n2_col]]),
                           studlab=studlab,
                           treat=list(treat1,treat2),
                           sm=sm)
        pairwise_dat[[i]] <- pair_dat[,1:9]                                   
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'TE'] <- paste0("TE", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'seTE'] <- paste0("seTE", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'event1'] <- paste0("event1", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'event2'] <- paste0("event2", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'n1'] <- paste0("n1", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'n2'] <- paste0("n2", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'treat_class1'] <- paste0("treat_class1", i)
        names(pairwise_dat[[i]])[names(pairwise_dat[[i]]) == 'treat_class2'] <- paste0("treat_class2", i)
        }
    ## extract extra columns (everything after column 9) and store in a list
    add_columns <- pair_dat[, c(3:5, 10:ncol(pair_dat)), drop = FALSE]
    extra_cols_list[[i]] <- add_columns
    }
    # pick the longest (max rows)
    combined_data <- do.call(rbind, extra_cols_list)
    new_cols <- combined_data[!duplicated(combined_data[c("studlab", "treat1", "treat2")]), ]
    final_dat = reduce(pairwise_dat, full_join, by = c("studlab","treat1","treat2"))
    final_dat <- final_dat %>% select(studlab, treat1, treat2, everything())
    final_dat1 <- left_join(
                            final_dat,
                            new_cols,
                            by = c("studlab", "treat1", "treat2")
                          )
    # # combine safely
    # final_dat1 <- cbind(final_dat, new_cols)

    names(final_dat1) <- c(names(final_dat), names(new_cols)[4:length(new_cols)])
    # Rename rob1/year1 back to rob/year (meta::pairwise adds "1" suffix to extra columns)
    names(final_dat1)[names(final_dat1) == 'rob1'] <- 'rob'
    names(final_dat1)[names(final_dat1) == 'year1'] <- 'year'

    return(final_dat1)
}