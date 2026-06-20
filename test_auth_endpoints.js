async function loginAndTest() {
    console.log("Testing with admin@cafepos.com / admin123 ...");
    let res = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'admin@cafepos.com', password: 'admin123' })
    });
    
    if (!res.ok) {
        console.log("Login failed!", await res.text());
        return;
    }
    const loginData = await res.json();
    const token = loginData.access_token || loginData.data?.access_token;
    console.log("Got token:", token ? "YES" : "NO");

    const endpoints = [
        '/categories',
        '/products',
        '/employees',
        '/payment-methods',
        '/customers',
        '/pos/orders?limit=100',
        '/pos/session/current',
    ];

    console.log("\n--- API Endpoint Tests ---");
    let allPassed = true;
    for (let ep of endpoints) {
        let r = await fetch(`http://localhost:8000${ep}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const body = await r.json();
        const count = Array.isArray(body.data) ? body.data.length : (body.data ? 1 : 0);
        const status = r.ok ? '✅' : '❌';
        console.log(`${status} [${r.status}] ${ep} => ${r.ok ? count + ' items' : body.detail || body.message}`);
        if (!r.ok) allPassed = false;
    }
    
    console.log("\n--- Data Shape Check (Products) ---");
    let prodRes = await fetch('http://localhost:8000/products', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const prodData = await prodRes.json();
    if (prodData.data && prodData.data.length > 0) {
        const p = prodData.data[0];
        console.log("Sample product fields:", Object.keys(p).join(', '));
        console.log("Has category_id:", 'category_id' in p);
        console.log("Has is_active:", 'is_active' in p);
        console.log("Has tax_percentage:", 'tax_percentage' in p);
    }

    console.log("\n--- Data Shape Check (Categories) ---");
    let catRes = await fetch('http://localhost:8000/categories', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const catData = await catRes.json();
    if (catData.data && catData.data.length > 0) {
        const c = catData.data[0];
        console.log("Sample category:", JSON.stringify(c));
    }

    console.log("\n" + (allPassed ? "✅ ALL ENDPOINTS PASS" : "❌ SOME ENDPOINTS FAILED"));
}

loginAndTest().catch(console.error);
