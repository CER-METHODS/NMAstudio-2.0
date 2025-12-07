/**
 * Browser compatibility warning script
 * Shows a warning banner to users not using Google Chrome
 */
(function() {
    // Detect Chrome (but not Edge which also contains "Chrome" in UA)
    var isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
    var isEdge = /Edg/.test(navigator.userAgent);
    
    // Only proceed if NOT Chrome (or is Edge)
    var shouldShowWarning = !isChrome || isEdge;
    
    // Function to show warning if element exists
    function showWarningIfExists() {
        if (!shouldShowWarning) return;
        
        var warning = document.getElementById('browser-warning');
        if (warning) {
            warning.style.display = 'block';
        }
    }
    
    // Use MutationObserver to detect when Dash renders the element
    function observeForElement() {
        if (!shouldShowWarning) return;
        
        // Check if already exists
        showWarningIfExists();
        
        // Set up observer for dynamically added elements
        var observer = new MutationObserver(function(mutations) {
            var warning = document.getElementById('browser-warning');
            if (warning) {
                warning.style.display = 'block';
                observer.disconnect(); // Stop observing once found
            }
        });
        
        // Start observing the document
        observer.observe(document.body || document.documentElement, {
            childList: true,
            subtree: true
        });
        
        // Fallback: disconnect after 10 seconds to prevent memory leaks
        setTimeout(function() {
            observer.disconnect();
        }, 10000);
    }
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', observeForElement);
    } else {
        observeForElement();
    }
    
    // Also check on multiple delays as fallback for Dash rendering
    setTimeout(showWarningIfExists, 500);
    setTimeout(showWarningIfExists, 1500);
    setTimeout(showWarningIfExists, 3000);
})();
