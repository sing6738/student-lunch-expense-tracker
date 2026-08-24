// date.ts
export function formatDateTH(date: Date | string): string {
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  return new Intl.DateTimeFormat('th-TH-u-ca-buddhist', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(d)
}

export function formatDateShortTH(date: Date | string): string {
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  return new Intl.DateTimeFormat('th-TH-u-ca-buddhist', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(d)
}

export function formatDateInput(date: Date | string): string {
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  return d.toISOString().split('T')[0]
}

export function parseDateInput(dateString: string): Date {
  return new Date(dateString)
}
