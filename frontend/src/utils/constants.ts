export const EXPENSE_CATEGORIES = [
  { value: 'rice', label: 'ข้าว/อาหารจานเดียว', icon: 'pi-bowl-rice' },
  { value: 'noodle', label: 'ก๋วยเตี๋ยว/เส้น', icon: 'pi-objects-column' }, // Alternative icon for chopsticks
  { value: 'snack', label: 'ของว่าง/ขนม', icon: 'pi-cookie' },
  { value: 'drink', label: 'เครื่องดื่ม', icon: 'pi-coffee' },
  { value: 'fruit', label: 'ผลไม้', icon: 'pi-apple' },
  { value: 'other', label: 'อื่นๆ', icon: 'pi-tag' },
]

export const CATEGORY_COLORS: Record<string, string> = {
  rice: '#F59E0B',
  noodle: '#3B82F6',
  snack: '#8B5CF6',
  drink: '#0EA5E9',
  fruit: '#10B981',
  other: '#64748B'
}

export const ORDER_STATUSES = [
  { value: 'ordered', label: 'สั่งแล้ว', color: 'warn' },
  { value: 'shipping', label: 'กำลังส่ง', color: 'info' },
  { value: 'delivered', label: 'ส่งถึงแล้ว', color: 'success' },
  { value: 'cancelled', label: 'ยกเลิก', color: 'danger' },
]
