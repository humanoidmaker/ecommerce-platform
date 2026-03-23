import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, CheckCircle, CreditCard, MapPin, Truck } from "lucide-react";
import { placeOrder, confirmPayment } from "@/api/checkoutApi";

const STEPS = ["Address", "Shipping", "Payment", "Review"];

export default function Checkout() {
  const [step, setStep] = useState(0);
  const [address, setAddress] = useState({ full_name: "", phone: "", address_line1: "", city: "", state: "", postal_code: "", country: "US" });
  const [shippingMethod, setShippingMethod] = useState("standard");
  const [loading, setLoading] = useState(false);
  const [orderId, setOrderId] = useState("");
  const [paymentId, setPaymentId] = useState("");
  const [orderNumber, setOrderNumber] = useState("");
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handlePlaceOrder = async () => {
    setLoading(true);
    try {
      const result = await placeOrder({ shipping_address: address, billing_address: address, shipping_method: shippingMethod, payment_method: "card" });
      setOrderId(result.order_id);
      setPaymentId(result.payment_id);
      setOrderNumber(result.order_number);
      setStep(3);
    } catch (e) { alert(e instanceof Error ? e.message : "Checkout failed"); }
    finally { setLoading(false); }
  };

  const handleConfirm = async () => {
    setLoading(true);
    try {
      const result = await confirmPayment(orderId, paymentId);
      if (result.success) { setSuccess(true); }
      else { alert("Payment failed. Please try again."); }
    } catch (e) { alert(e instanceof Error ? e.message : "Payment failed"); }
    finally { setLoading(false); }
  };

  if (success) {
    return (
      <div className="max-w-md mx-auto px-4 py-20 text-center">
        <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Order Placed!</h1>
        <p className="text-gray-500 mb-1">Order #{orderNumber}</p>
        <p className="text-sm text-gray-400 mb-6">You will receive a confirmation email shortly.</p>
        <button onClick={() => navigate("/orders")} className="bg-blue-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-blue-700">View Orders</button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Stepper */}
      <div className="flex items-center gap-2 mb-8">
        {STEPS.map((s, i) => (
          <div key={s} className="flex items-center gap-2">
            <div className={`h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold ${i <= step ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-500"}`}>{i + 1}</div>
            <span className={`text-sm ${i <= step ? "text-gray-900 font-medium" : "text-gray-400"}`}>{s}</span>
            {i < STEPS.length - 1 && <div className="flex-1 h-px bg-gray-200 mx-2" />}
          </div>
        ))}
      </div>

      {/* Step 1: Address */}
      {step === 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-bold flex items-center gap-2"><MapPin className="h-5 w-5" /> Shipping Address</h2>
          {["full_name", "phone", "address_line1", "city", "state", "postal_code"].map(f => (
            <input key={f} value={(address as Record<string, string>)[f]} onChange={e => setAddress(prev => ({ ...prev, [f]: e.target.value }))}
              placeholder={f.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())} className="w-full h-10 px-3 rounded-lg border border-gray-200 text-sm" />
          ))}
          <button onClick={() => setStep(1)} disabled={!address.full_name || !address.address_line1}
            className="w-full h-11 bg-blue-600 text-white rounded-xl font-medium disabled:opacity-50">Continue to Shipping</button>
        </div>
      )}

      {/* Step 2: Shipping */}
      {step === 1 && (
        <div className="space-y-4">
          <h2 className="text-lg font-bold flex items-center gap-2"><Truck className="h-5 w-5" /> Shipping Method</h2>
          {[{ method: "standard", name: "Standard (5-7 days)", price: "$5.99" }, { method: "express", name: "Express (2-3 days)", price: "$12.99" }, { method: "overnight", name: "Overnight (1 day)", price: "$24.99" }].map(s => (
            <label key={s.method} className={`flex items-center gap-3 p-4 border rounded-xl cursor-pointer ${shippingMethod === s.method ? "border-blue-500 bg-blue-50" : "border-gray-200"}`}>
              <input type="radio" name="shipping" checked={shippingMethod === s.method} onChange={() => setShippingMethod(s.method)} className="text-blue-600" />
              <span className="flex-1 text-sm font-medium">{s.name}</span>
              <span className="text-sm font-bold">{s.price}</span>
            </label>
          ))}
          <div className="flex gap-3">
            <button onClick={() => setStep(0)} className="flex-1 h-11 border border-gray-200 rounded-xl text-sm">Back</button>
            <button onClick={() => setStep(2)} className="flex-1 h-11 bg-blue-600 text-white rounded-xl font-medium">Continue to Payment</button>
          </div>
        </div>
      )}

      {/* Step 3: Payment */}
      {step === 2 && (
        <div className="space-y-4">
          <h2 className="text-lg font-bold flex items-center gap-2"><CreditCard className="h-5 w-5" /> Payment</h2>
          <input placeholder="Card Number" defaultValue="4242 4242 4242 4242" className="w-full h-10 px-3 rounded-lg border border-gray-200 text-sm" />
          <div className="grid grid-cols-2 gap-3">
            <input placeholder="MM/YY" defaultValue="12/28" className="h-10 px-3 rounded-lg border border-gray-200 text-sm" />
            <input placeholder="CVV" defaultValue="123" className="h-10 px-3 rounded-lg border border-gray-200 text-sm" />
          </div>
          <p className="text-xs text-gray-400">This is a mock payment — no real charge.</p>
          <div className="flex gap-3">
            <button onClick={() => setStep(1)} className="flex-1 h-11 border border-gray-200 rounded-xl text-sm">Back</button>
            <button onClick={handlePlaceOrder} disabled={loading} className="flex-1 h-11 bg-blue-600 text-white rounded-xl font-medium flex items-center justify-center gap-2 disabled:opacity-50">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Place Order"}
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Confirm */}
      {step === 3 && (
        <div className="space-y-4 text-center">
          <h2 className="text-lg font-bold">Confirm Payment</h2>
          <p className="text-sm text-gray-500">Order #{orderNumber} is ready. Click below to confirm payment.</p>
          <button onClick={handleConfirm} disabled={loading} className="w-full h-11 bg-green-600 text-white rounded-xl font-medium flex items-center justify-center gap-2 disabled:opacity-50">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Confirm & Pay"}
          </button>
        </div>
      )}
    </div>
  );
}
