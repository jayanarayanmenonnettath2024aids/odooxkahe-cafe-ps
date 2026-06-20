// End-to-end test of the new POS flow
async function testPOSFlow() {
    // Login
    const res = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'admin@cafepos.com', password: 'admin123' })
    });
    const { access_token } = await res.json();
    const h = { 'Authorization': `Bearer ${access_token}`, 'Content-Type': 'application/json' };

    console.log('=== POS Flow Test ===\n');

    // 1. Get current session
    console.log('1. Getting current session...');
    let session;
    try {
        const r = await fetch('http://localhost:8000/pos/session/current', { headers: h });
        session = (await r.json()).data;
        console.log(`   ✅ Session ID: ${session.id}, Status: ${session.status}`);
    } catch(e) {
        console.log('   Creating new session...');
        const r = await fetch('http://localhost:8000/pos/session/open', {
            method: 'POST', headers: h,
            body: JSON.stringify({ opening_balance: 0 })
        });
        session = (await r.json()).data;
        console.log(`   ✅ New Session ID: ${session.id}`);
    }

    // 2. Get products to find IDs
    console.log('2. Getting products...');
    const prodsRes = await fetch('http://localhost:8000/products', { headers: h });
    const prods = (await prodsRes.json()).data;
    const p1 = prods[0], p2 = prods[1];
    console.log(`   ✅ Got ${prods.length} products. Using: ${p1.name} (₹${p1.price}) + ${p2.name} (₹${p2.price})`);

    // 3. Create order with items (the new POST /pos/orders endpoint)
    console.log('3. Creating order with items...');
    const orderRes = await fetch('http://localhost:8000/pos/orders', {
        method: 'POST', headers: h,
        body: JSON.stringify({
            session_id: session.id,
            order_type: 'TAKEAWAY',
            items: [
                { product_id: p1.id, quantity: 2 },
                { product_id: p2.id, quantity: 1 }
            ]
        })
    });
    if (!orderRes.ok) {
        console.log(`   ❌ Failed: ${await orderRes.text()}`);
        return;
    }
    const order = (await orderRes.json()).data;
    console.log(`   ✅ Order created! ID: ${order.id}, Items: ${order.items.length}, Total: ₹${order.total_amount}`);

    // 4. Send to kitchen (the new POST /pos/cart/{id}/send-to-kitchen)
    console.log('4. Sending to kitchen...');
    const kitchenRes = await fetch(`http://localhost:8000/pos/cart/${order.id}/send-to-kitchen`, {
        method: 'POST', headers: h
    });
    if (!kitchenRes.ok) {
        console.log(`   ❌ Failed: ${await kitchenRes.text()}`);
        return;
    }
    const kitchenOrder = (await kitchenRes.json()).data;
    console.log(`   ✅ Order sent to kitchen! Status: ${kitchenOrder.status}`);

    // 5. Pay (the new POST /pos/receipt/{id}/pay)
    console.log('5. Processing payment...');
    const payRes = await fetch(`http://localhost:8000/pos/receipt/${order.id}/pay`, {
        method: 'POST', headers: h,
        body: JSON.stringify({
            payment_method_type: 'cash',
            amount: order.total_amount,
            transaction_reference: `TEST-${Date.now()}`
        })
    });
    if (!payRes.ok) {
        console.log(`   ❌ Failed: ${await payRes.text()}`);
        return;
    }
    const payResult = await payRes.json();
    console.log(`   ✅ Payment successful! ${payResult.message}`);

    console.log('\n✅ FULL POS FLOW WORKS END-TO-END!');
    
    // 6. Test direct payment (skipping send-to-kitchen, like completePayment without sendToKitchen first)
    console.log('\n6. Testing direct payment (DRAFT → PAID)...');
    const order2Res = await fetch('http://localhost:8000/pos/orders', {
        method: 'POST', headers: h,
        body: JSON.stringify({
            session_id: session.id,
            order_type: 'TAKEAWAY',
            items: [{ product_id: p1.id, quantity: 1 }]
        })
    });
    const order2 = (await order2Res.json()).data;
    console.log(`   Created order ${order2.id} in status: ${order2.status}`);
    
    const pay2Res = await fetch(`http://localhost:8000/pos/receipt/${order2.id}/pay`, {
        method: 'POST', headers: h,
        body: JSON.stringify({
            payment_method_type: 'cash',
            amount: order2.total_amount,
            transaction_reference: `TEST2-${Date.now()}`
        })
    });
    if (!pay2Res.ok) {
        console.log(`   ❌ Direct pay failed: ${await pay2Res.text()}`);
    } else {
        const pay2 = await pay2Res.json();
        console.log(`   ✅ Direct payment worked! ${pay2.message}`);
    }
}

testPOSFlow().catch(console.error);
