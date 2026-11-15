import Bridge
import Lean

open Bridge Lean

def packetFromJson (j : Json) : Except String Packet := do
  return {
    model := ← (← j.getObjVal? "model").getStr?
    policyId := ← (← j.getObjVal? "policyId").getStr?
    sourceId := ← (← j.getObjVal? "sourceId").getStr?
    quote := ← (← j.getObjVal? "quote").getStr?
    factId := ← (← j.getObjVal? "factId").getStr?
    choice := ← (← j.getObjVal? "choice").getStr?
    refundBps := ← (← j.getObjVal? "refundBps").getNat?
    reviewBps := ← (← j.getObjVal? "reviewBps").getNat?
    noneBps := ← (← j.getObjVal? "noneBps").getNat?
    supportNoulBps := ← (← j.getObjVal? "supportNoulBps").getNat?
    risk0Bps := ← (← j.getObjVal? "risk0Bps").getNat?
    risk1Bps := ← (← j.getObjVal? "risk1Bps").getNat?
    risk2Bps := ← (← j.getObjVal? "risk2Bps").getNat?
  }

def main (args : List String) : IO UInt32 := do
  match args with
  | [] =>
    IO.println s!"Synthetic replay: {repr (evaluate demoPolicy demoPacket)}"
    IO.println "24 Lean regression examples and 12 named theorems compile in Bridge."
    return 0
  | [path] =>
    let raw ← IO.FS.readFile path
    match Json.parse raw >>= packetFromJson with
    | .error err =>
      IO.eprintln s!"Invalid packet: {err}"
      return 2
    | .ok packet =>
      let result := evaluate demoPolicy packet
      let label := match result with
        | .accepted => "accepted"
        | .review => "review"
        | .invalid => "invalid"
      IO.println (Json.mkObj [("decision", Json.str label),
        ("policy", Json.str demoPolicy.id),
        ("scope", Json.str "synthetic reviewed refund fixture only")]).compress
      return if result == .invalid then 2 else 0
  | _ =>
    IO.eprintln "Usage: lake exe bridge [normalized-packet.json]"
    return 2
