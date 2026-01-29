import { useState } from "react";
import Login from "./pages/Login";
import OtpVerify from "./pages/OtpVerify";
import Slots from "./pages/Slots";
import Queue from "./pages/Queue";

function App() {
  const [step, setStep] = useState("login");
  const [email, setEmail] = useState("");
  const [slot, setSlot] = useState("");

  return (
    <>
      {step === "login" && <Login onNext={(e) => {
        setEmail(e);
        setStep("otp");
      }} />}

      {step === "otp" && (
        <OtpVerify email={email} onSuccess={() => setStep("slots")} />
      )}

      {step === "slots" && (
        <Slots email={email} onBooked={(s) => {
          setSlot(s);
          setStep("queue");
        }} />
      )}

      {step === "queue" && <Queue slot={slot} />}
    </>
  );
}

export default App;
