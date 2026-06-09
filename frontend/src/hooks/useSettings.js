/**
 * Kullanıcı model tercihlerini localStorage'dan okur/yazar.
 * Tüm bileşenler bu hook ile aynı ayarlara erişir.
 */
export function getSettings() {
  try {
    return {
      holdThres: parseFloat(localStorage.getItem('fw_hold_thres') || '0.65'),
      holdExpl:  localStorage.getItem('fw_hold_expl') || 'Orta',
    }
  } catch {
    return { holdThres: 0.65, holdExpl: 'Orta' }
  }
}

export function saveSettings({ holdThres, holdExpl }) {
  try {
    localStorage.setItem('fw_hold_thres', String(holdThres))
    localStorage.setItem('fw_hold_expl',  holdExpl)
  } catch {}
}
