// 2레벨 VSC: DC 링크(중점 0), 레그 3개(스위치 6개 + 역병렬 다이오드), Y 결선 부하(중성점 n)
const F = Fig(1150, 680); patchInductorV(F);
drawVSC(F, null);
F.done();
