// Initialize dash_clientside if it doesn't exist
if (!window.dash_clientside) {
    window.dash_clientside = {};
}

// Initialize clientside namespace if it doesn't exist
if (!window.dash_clientside.clientside) {
    window.dash_clientside.clientside = {};
}

// Add the logStorageChanges function
window.dash_clientside.clientside.logStorageChanges = function(...args) {
    // Get all store IDs from the callback context
    // The last half of args are State values, first half minus one are Input values
    const numStores = Math.floor(args.length / 2);
    const storeData = args.slice(numStores);
    
    // Get storage keys from dcc.Store components
    const stores = document.querySelectorAll('[id$="_STORAGE"]');
    
    console.log('%c=== LocalStorage Debug (_STORAGE items) ===', 'color: #00ab9c; font-weight: bold; font-size: 14px;');
    console.log('%cTimestamp: ' + new Date().toISOString(), 'color: #666;');
    console.log('');
    
    // Log each store's data
    stores.forEach((store, index) => {
        const storeId = store.id;
        const data = storeData[index];
        
        if (data !== null && data !== undefined) {
            console.log(`%c${storeId}:`, 'color: #1EAEDB; font-weight: bold;');
            console.log(data);
        } else {
            console.log(`%c${storeId}:`, 'color: #999;');
            console.log('  (empty)');
        }
    });
    
    console.log('%c' + '='.repeat(50), 'color: #00ab9c;');
    console.log('');
    
    // Return empty string to satisfy the Output
    return '';
};
