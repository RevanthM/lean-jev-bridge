import Bridge.Kernel

namespace Bridge

example : evaluate demoPolicy demoPacket = .accepted := by decide
example : evaluate { demoPolicy with reviewedFact := false } demoPacket = .review := by decide
example : evaluate demoPolicy { demoPacket with quote := "invented evidence" } = .review := by decide
example : evaluate demoPolicy { demoPacket with sourceId := "wrong-document" } = .review := by decide
example : evaluate demoPolicy { demoPacket with factId := "wrong-fact" } = .review := by decide
example : evaluate demoPolicy { demoPacket with policyId := "wrong-policy" } = .review := by decide
example : evaluate { demoPolicy with day := 20261201 } demoPacket = .review := by decide
example : evaluate { demoPolicy with day := 20261031 } demoPacket = .review := by decide
example : evaluate demoPolicy { demoPacket with refundBps := 9799, reviewBps := 191 } = .review := by decide
example : evaluate demoPolicy { demoPacket with refundBps := 9800, reviewBps := 190 } = .accepted := by decide
example : evaluate demoPolicy { demoPacket with supportNoulBps := 9799 } = .review := by decide
example : evaluate demoPolicy { demoPacket with supportNoulBps := 9800 } = .accepted := by decide
example : evaluate demoPolicy { demoPacket with risk0Bps := 9499, risk1Bps := 501, risk2Bps := 0 } = .review := by decide
example : evaluate demoPolicy { demoPacket with risk0Bps := 9500, risk1Bps := 500, risk2Bps := 0 } = .accepted := by decide
example : evaluate demoPolicy { demoPacket with refundBps := 10001 } = .invalid := by decide
example : evaluate demoPolicy { demoPacket with supportNoulBps := 10001 } = .invalid := by decide
example : evaluate demoPolicy { demoPacket with risk0Bps := 10001 } = .invalid := by decide
example : evaluate demoPolicy { demoPacket with choice := "none" } = .review := by decide
example : evaluate demoPolicy { demoPacket with choice := "review" } = .review := by decide
example : evaluate demoPolicy { demoPacket with choice := "arbitrary-action" } = .invalid := by decide
example : evaluate demoPolicy { demoPacket with model := "jev-latest" } = .invalid := by decide
example : evaluate demoPolicy { demoPacket with model := "jev-1.13.0" } = .invalid := by decide
example : evaluate { demoPolicy with sourceLine := "" } { demoPacket with quote := "" } = .review := by decide
example : evaluate { demoPolicy with reviewedFact := false } { demoPacket with refundBps := 10000, reviewBps := 0, noneBps := 0, supportNoulBps := 10000, risk0Bps := 10000, risk1Bps := 0, risk2Bps := 0 } = .review := by decide

end Bridge
