import { formatTHB, formatNumberTH } from '@/utils/currency'
import { formatDateTH, formatDateShortTH, formatDateInput } from '@/utils/date'

export function useFormat() {
  return {
    formatTHB,
    formatNumberTH,
    formatDateTH,
    formatDateShortTH,
    formatDateInput
  }
}
