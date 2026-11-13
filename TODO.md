# To do (next session)

Open questions for outside groups and decisions are in `OPEN_QUESTIONS.md`; this is our own work list.

- [ ] Validate the electron and photon setup against the EGM Run-3 recommendations (IDs, scale and smearing, SFs).
- [ ] Validate the jet setup against the JME Run-3 recommendations (JEC/JER, jet ID, PUPPI, vetomaps).
- [ ] W tag: the neutrino (MET-based reconstruction; the W candidate now uses MET with p_z = 0).
- [ ] W tag: the W boson (definition and its NANO output).
- [ ] Loose-selection pair bias (`simulation/configs/ZX_test.yaml`): only the dilepton pair closest to the Z mass among the loose (ID-less) objects is stored, so tighter IDs/isolation applied offline do not reproduce a tight selection exactly. Study the size of the effect, probably by storing the selected pair for each of several IDs/selections.
- [ ] Validate and document carefully the NANO contents and format. The documentation is in `simulation/NANO.md`; still to do: a systematic validation of every table.
