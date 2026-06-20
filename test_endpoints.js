

async function checkUrl(url) {
    try {
        const res = await fetch(`http://localhost:8000${url}`);
        console.log(`[${res.status}] ${url}`);
        if (!res.ok) {
            console.log(`Error body: ${await res.text()}`);
        }
    } catch (e) {
        console.log(`[ERROR] ${url}: ${e.message}`);
    }
}

async function run() {
    await checkUrl('/categories');
    await checkUrl('/products');
    await checkUrl('/employees');
    await checkUrl('/payment-methods');
    await checkUrl('/customers');
    await checkUrl('/pos/orders?limit=100');
    await checkUrl('/pos/session/current');
    await checkUrl('/pos/floors');
}

run();
