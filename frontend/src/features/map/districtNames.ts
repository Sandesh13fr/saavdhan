export function normalizeDistrict(name: string): string {
  const key = name.toLowerCase().replace(/[^a-z]/g, '');
  const aliases: Record<string, string> = {
    aurangabad: 'chhatrapatisambhajinagar',
    chhatrapatisambhajinagar: 'chhatrapatisambhajinagar',
    chatrapatisambhajinagar: 'chhatrapatisambhajinagar',
    ahmednagar: 'ahilyanagar',
    ahmadnagar: 'ahilyanagar',
    ahilyanagar: 'ahilyanagar',
    mumbai: 'mumbaicity',
    bombay: 'mumbaicity',
    mumbaisub: 'mumbaisuburban',
    raigarh: 'raigad',
    bid: 'beed',
    buldana: 'buldhana',
    gondiya: 'gondia',
    osmanabad: 'dharashiv',
  };
  return aliases[key] ?? key;
}
