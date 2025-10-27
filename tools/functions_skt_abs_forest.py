import pandas as pd
from tools.kt_table_advance import *
from tools.functions_skt_forestplot import __skt_ab_forstplot, __skt_options_forstplot, __skt_mix_forstplot

def __Change_Abs(value_effect, value_change,lower,rowData):
    
    data = pd.read_csv('db/skt/final_all.csv')
    p_score = pd.read_csv('db/ranking/rank.csv')
    long_dat = pd.read_csv('db/psoriasis_long_complete.csv')
    long_dat = pd.DataFrame(long_dat)

    range_ref_ab = long_dat.groupby('treat').apply(
        lambda group: pd.Series({
            "min_value": (group["rPASI90"] / group["nPASI90"]).min() * 1000,
            "max_value": (group["rPASI90"] / group["nPASI90"]).max() * 1000
        })
    ).reset_index()

    df = pd.DataFrame(data)
    df['Certainty']= ''
    df['within_study'] = ''
    df['reporting'] = ''
    df['indirectness'] = ''
    df['imprecision'] = ''
    df['heterogeneity'] = ''
    df['incoherence'] = ''

    for i in range(df.shape[0]):
        src = df['Reference'][i]
        trgt = df['Treatment'][i]
        slctd_comps = [f'{src}:{trgt}']
        slctd_compsinv = [f'{trgt}:{src}']
        cinima_df = cinima_dat[cinima_dat['Comparison'].isin(slctd_comps) | cinima_dat['Comparison'].isin(slctd_compsinv)]
        df['Certainty'][i] = cinima_df['Confidence rating'].iloc[0]
        df['within_study'][i] = cinima_df['Within-study bias'].iloc[0]
        df['reporting'][i] = cinima_df['Reporting bias'].iloc[0]
        df['indirectness'][i] = cinima_df['Indirectness'].iloc[0]
        df['imprecision'][i] = cinima_df['Imprecision'].iloc[0]
        df['heterogeneity'][i] = cinima_df['Heterogeneity'].iloc[0]
        df['incoherence'][i] = cinima_df['Incoherence'].iloc[0]
        df['Comments'] = ['' for _ in range(df.shape[0])]
        df['CI_width_hf'] = df.CI_upper - df['RR']
        df['lower_error'] = df['RR'] - df.CI_lower
        df['weight'] = 1/df['CI_width_hf']
        df = df.round(2)
    df['Graph'] = ''
    df['risk'] = 'Enter a number'
    df['Scale_lower'] = 'Enter a value for lower'
    df['Scale_upper'] = 'Enter a value for upper'
    # df['ab_effect'] = ''
    df['ab_difference'] = ''
    df['rationality'] = 'Enter a reason'

    # print(value_change[0]['value'], value_change[0]['colId']) if value_change is not None else 0
    refer_name = None
    if value_change is not None and value_change[0]['value'] is not None and value_change[0]['value'] != 'Enter a value for lower' and value_change[0]['colId']=='Scale_lower':
        refer_name = value_change[0]['data']['Reference']
        scale_lower = float(value_change[0]['value'])
        scale_upper = float(value_change[0]['data']['Scale_upper']) if value_change[0]['data']['Scale_upper'] != 'Enter a value for upper' else None
    elif value_change is not None and value_change[0]['value'] is not None:
        refer_name = value_change[0]['data']['Reference']
        scale_lower = float(value_change[0]['data']['Scale_lower']) if value_change[0]['data']['Scale_lower'] != 'Enter a value for lower' else None
    else:
        scale_lower = None
        refer_name = refer_name

    if value_change is not None and value_change[0]['value'] is not None and value_change[0]['value'] != 'Enter a value for upper' and value_change[0]['colId']=='Scale_upper':
        refer_name = value_change[0]['data']['Reference']
        scale_upper = float(value_change[0]['value'])
        scale_lower = float(value_change[0]['data']['Scale_lower']) if value_change[0]['data']['Scale_lower'] != 'Enter a value for lower' else None
    elif value_change is not None and value_change[0]['value'] is not None:
        refer_name = value_change[0]['data']['Reference']
        scale_upper = float(value_change[0]['data']['Scale_upper']) if value_change[0]['data']['Scale_upper'] != 'Enter a value for upper' else None
    else:
        scale_upper = None
        refer_name = refer_name

    # if value_change is not None and value_change[0]['value'] is not None and (value_change[0]['value'] != 'Enter a value for upper' and value_change[0]['value'] != 'Enter a value for lower') and (value_change[0]['colId']=='Scale_upper' or value_change[0]['colId']=='Scale_lower'):
    if value_change is not None and value_change[0]['value'] is not None and value_change[0]['colId']=='risk':
        refer_name = value_change[0]['data']['Reference']
        risk = int(value_change[0]['value'])
    else:
        refer_name = refer_name
        risk = None
        
    # if value_effect==[]:
    #         df = __skt_mix_forstplot(df,lower, scale_lower, scale_upper, refer_name)
    # elif all(effect in value_effect for effect in ['PI', 'direct', 'indirect']):
    #         df = __skt_all_forstplot(df,lower, scale_lower, scale_upper, refer_name)
    # elif all(effect in ['PI'] for effect in value_effect):
    #     
    #     df = __skt_PI_forstplot(df,lower, scale_lower, scale_upper, refer_name)
    # elif all(effect in ['direct'] for effect in value_effect):
    #         df = __skt_direct_forstplot(df,lower, scale_lower, scale_upper, refer_name)
    # elif all(effect in ['indirect'] for effect in value_effect):
    #         df = __skt_indirect_forstplot(df,lower, scale_lower, scale_upper, refer_name)
    # elif all(effect in ['PI', 'direct'] for effect in value_effect):
    #         df = __skt_PIdirect_forstplot(df,lower, scale_lower, scale_upper, refer_name)
    # elif all(effect in ['PI', 'indirect'] for effect in value_effect):
    #         df = __skt_PIindirect_forstplot(df,lower, scale_lower, scale_upper, refer_name)
    # elif all(effect in ['direct', 'indirect'] for effect in value_effect):
    #         df = __skt_directin_forstplot(df,lower, scale_lower, scale_upper, refer_name)
    # print(df['risk'])
    
    # if toggle_value:
    #     df = __skt_ab_forstplot(risk, value_effect, df,lower, scale_lower, scale_upper, refer_name)
    # else:
    if value_effect==[]:
            df = __skt_mix_forstplot(df,lower, scale_lower, scale_upper, refer_name)
    else:
            df = __skt_options_forstplot(value_effect,df,lower, scale_lower, scale_upper, refer_name)

    grouped = df.groupby(["Reference", "risk", 'Scale_lower', 'Scale_upper'])
    rowData_effect = []
    for (ref, risk, Scale_lower, Scale_upper), group in grouped:
        treatments = []
        for _, row in group.iterrows():
            treatment_data = {"Treatment": row["Treatment"], 
                            "RR": row["RR"], "direct": row["direct"],
                            "Graph": row["Graph"], "indirect": row["indirect"],
                            "p-value": row["p-value"], "Certainty": row["Certainty"],
                            "direct_low": row["direct_low"],"direct_up": row["direct_up"],
                            "indirect_low": row["indirect_low"],"indirect_up": row["indirect_up"],
                            "CI_lower": row["CI_lower"],"CI_upper": row["CI_upper"],
                            "Comments": row["Comments"],
                            # "ab_effect": row["ab_effect"],
                          "ab_difference": row["ab_difference"],
                          "within_study": row["within_study"],"reporting": row["reporting"],
                          "indirectness": row["indirectness"],"imprecision": row["imprecision"],
                          "heterogeneity": row["heterogeneity"],"incoherence": row["incoherence"],
                            }
            treatments.append(treatment_data)
        rowData_effect.append({"Reference": ref, "risk": risk,
                    'Scale_lower': Scale_lower ,
                    'Scale_upper': Scale_upper ,"Treatments": treatments})

    rowData_effect = pd.DataFrame(rowData_effect)
    rowData_effect = rowData_effect.merge(p_score, left_on='Reference', right_on='treatment', how='left')
    rowData_effect = rowData_effect.merge(range_ref_ab, left_on='Reference', right_on='treat', how='left')
    rowData_effect['risk_range'] = rowData_effect.apply(
        lambda row: f"from {int(row['min_value'])} to {int(row['max_value'])}",
        axis=1
    )
    
    # for i in range(min(5, len(rowData_effect))):  
    #     print(rowData_effect.loc[i, 'Treatments'][1]['RR'])

    dfc_2 = rowData_effect.copy()   
    
    rowData = pd.DataFrame(rowData)
    dfc = rowData.copy()
    round(dfc,2)

    dfc.reset_index(drop=True, inplace=True)  
    for row_idx in range(dfc.shape[0]):
        detail_data = dfc.loc[row_idx, 'Treatments']
        detail_data = pd.DataFrame(detail_data)
        for i in range(0,detail_data.shape[0]):
            # dfc.loc[i,'Reference'] = f"{dfc.loc [i,'Reference']}" + f"\n{value_risk} per 1000"
            dfc.loc[row_idx,'Treatments'][i]['Graph'] = dfc_2.loc[row_idx,'Treatments'][i]['Graph']
            
    dfc = pd.DataFrame(dfc)

    if value_change is not None and value_change[0]['value'] is not None and value_change[0]['value'] != 'Enter a number' and value_change[0]['colId']=='risk':
        
        row_idx = value_change[0]['rowIndex']
        # print(row_idx)
        # rowData = pd.DataFrame(rowData)
        # dfc = rowData.copy()
        round(dfc,2)

        dfc.reset_index(drop=True, inplace=True)  
        dfc.loc[row_idx,'risk']=value_change[0]['value']
        value_risk = int(value_change[0]['value'])
        
        orig_data = dfc.loc[row_idx, 'Treatments']
        orig_data = pd.DataFrame(orig_data)
        reference = dfc.loc[row_idx, 'Reference']
        # print(reference)

        detail_data = row_data.loc[row_data['Reference'] == reference, 'Treatments'].iloc[0]
        # detail_data = row_data.loc[row_idx, 'Treatments']
        detail_data = pd.DataFrame(detail_data)
        # print(detail_data.head(3))
        
        for i in range(1,detail_data.shape[0]):
            treat = orig_data.loc[i,'Treatment']
            # print(treat)
            risk_treat = value_risk*detail_data.loc[detail_data['Treatment'] == treat, 'RR']
            # value_risk*detail_data['RR'].loc[i]
            # value_risk*detail_data.loc[detail_data['Treatment'] == treat, 'RR']
            # if i==1: print(detail_data.loc[detail_data['Treatment'] == treat, 'RR'])
            risk_treat = int(risk_treat)
            abrisk = risk_treat-value_risk 
            # dfc.loc[i,'Reference'] = f"{dfc.loc [i,'Reference']}" + f"\n{value_risk} per 1000"
            # dfc.loc[row_idx,'Treatments'][i]['Treatment'] = f"{row_data.loc[row_idx,'Treatments'][i]['Treatment']}" + f"\n{risk_treat} per 1000"
            
            # dfc.loc[row_idx,'Treatments'][i]['RR'] = str(row_data.loc[row_idx,'Treatments'][i]['RR'])+ '\n(' + str(row_data.loc[row_idx,'Treatments'][i]['CI_lower']) + ', ' + str(row_data.loc[row_idx,'Treatments'][i]['CI_upper']) + ')'
            # dfc.loc[row_idx,'Treatments'][i]['RR'] = f"{dfc.loc[row_idx,'Treatments'][i]['RR']}" + (f"\n{abrisk} more per 1000" if abrisk > 0 else f"\n{abs(abrisk)} less per 1000")
            
            # dfc.loc[row_idx,'Treatments'][i]['ab_effect'] = f"\n{risk_treat} per 1000"
            dfc.loc[row_idx,'Treatments'][i]['ab_difference'] = f"{abrisk} more per 1000" if abrisk > 0 else f"\n{abs(abrisk)} less per 1000"
            
            
            direct_value = row_data.loc[row_idx, 'Treatments'][i]['direct']
            direct_low = row_data.loc[row_idx, 'Treatments'][i]['direct_low']
            direct_up = row_data.loc[row_idx, 'Treatments'][i]['direct_up']

            dfc.loc[row_idx, 'Treatments'][i]['direct'] = (
                f"{direct_value}\n({direct_low}, {direct_up})"
                if pd.notna(direct_value) 
                else ""
            )
            # dfc.loc[row_idx,'Treatments'][i]['direct'] = f"{row_data.loc[row_idx,'Treatments'][i]['direct']}" + f"\n({row_data.loc[row_idx,'Treatments'][i]['direct_low']}, {row_data.loc[row_idx,'Treatments'][i]['direct_up']})" if pd.notna(row_data.loc[row_idx,'Treatments'][i]['direct']) else ""
            indirect_value = row_data.loc[row_idx, 'Treatments'][i]['indirect']
            indirect_low = row_data.loc[row_idx, 'Treatments'][i]['indirect_low']
            indirect_up = row_data.loc[row_idx, 'Treatments'][i]['indirect_up']

            dfc.loc[row_idx, 'Treatments'][i]['indirect'] = (
                f"{indirect_value}\n({indirect_low}, {indirect_up})"
                if pd.notna(indirect_value) 
                else ""
            )
            # dfc.loc[row_idx,'Treatments'][i]['indirect'] = f"{row_data.loc[row_idx,'Treatments'][i]['indirect']}" + f"\n({row_data.loc[row_idx,'Treatments'][i]['indirect_low']}, {row_data.loc[row_idx,'Treatments'][i]['indirect_up']})" if pd.notna(row_data.loc[row_idx,'Treatments'][i]['indirect']) else ""

            abs_value = f"\n{abrisk} more per 1000" if abrisk > 0 else f"\n{abs(abrisk)} less per 1000"
            
            risk_low = value_risk*detail_data['CI_lower'].loc[i]
            # print(detail_data['CI_lower'].loc[i])
            risk_low =int(risk_low)
            ablow = risk_low-value_risk
            abs_low = f"{ablow} more per 1000" if ablow  > 0 else f"{abs(ablow)} less per 1000"

            risk_up = value_risk*detail_data['CI_upper'].loc[i]
            risk_up =int(risk_up)
            abup = risk_up-value_risk
            abs_up = f"{abup} more per 1000" if abup  > 0 else f"{abs(abup)} less per 1000"

            dfc.loc[row_idx, 'Treatments'][i]['ab_difference'] = f"{abs_value}\n({abs_low} to {abs_up})"
            # print(dfc.loc[row_idx, 'Treatments'][i]['ab_difference'])

       
        dfc = pd.DataFrame(dfc)
        # n_row = dfc.shape[0]
    
        return dfc.to_dict("records")

    return dfc.to_dict("records")

