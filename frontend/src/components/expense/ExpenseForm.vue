<script setup lang="ts">
import { useForm, useField } from 'vee-validate'
import * as zod from 'zod'
import { toTypedSchema } from '@vee-validate/zod'
import { EXPENSE_CATEGORIES } from '@/utils/constants'
import RestaurantSelector from '@/components/restaurant/RestaurantSelector.vue'
import MenuSelector from '@/components/restaurant/MenuSelector.vue'
import { formatDateInput } from '@/utils/date'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import Textarea from 'primevue/textarea'

interface Props {
  initialData?: any
  isEditing?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  initialData: () => ({}),
  isEditing: false,
})

const emit = defineEmits<{
  submit: [data: any]
  cancel: []
}>()

const validationSchema = toTypedSchema(zod.object({
  restaurant_id: zod.number().min(1, 'กรุณาเลือกร้านอาหาร'),
  menu_id: zod.number().min(1, 'กรุณาเลือกเมนู'),
  amount: zod.number().min(0.01, 'จำนวนเงินต้องมากกว่า 0').max(10000, 'จำนวนเงินสูงเกินไป'),
  category: zod.enum(['rice', 'noodle', 'snack', 'drink', 'fruit', 'other']),
  date: zod.string().refine(val => !isNaN(new Date(val).getTime()), 'วันที่ไม่ถูกต้อง'),
  note: zod.string().max(500).optional(),
}))

const { handleSubmit, setFieldValue, errors, isSubmitting } = useForm({
  validationSchema,
  initialValues: {
    restaurant_id: props.initialData?.restaurant_id || null,
    menu_id: props.initialData?.menu_id || null,
    amount: props.initialData?.amount || '',
    category: props.initialData?.category || 'rice',
    date: props.initialData?.date ? formatDateInput(props.initialData.date) : formatDateInput(new Date()),
    note: props.initialData?.note || '',
  },
})

const { value: restaurant_id } = useField<number>('restaurant_id')
const { value: menu_id } = useField<number>('menu_id')
const { value: amount } = useField<number>('amount')
const { value: category } = useField<string>('category')
const { value: date } = useField<string>('date')
const { value: note } = useField<string>('note')

const onSubmit = handleSubmit((values) => {
  emit('submit', values)
})

function handleRestaurantChange(restaurantId: number | null) {
  if (restaurantId !== restaurant_id.value) {
    setFieldValue('restaurant_id', restaurantId)
    setFieldValue('menu_id', null)
  }
}
</script>

<template>
  <form @submit.prevent="onSubmit" class="expense-form">
    <div class="form-grid">
      <div class="form-field">
        <label>ร้านอาหาร <span class="required">*</span></label>
        <RestaurantSelector v-model="restaurant_id" @change="handleRestaurantChange" :disabled="isSubmitting" />
      </div>

      <div class="form-field">
        <label>เมนู <span class="required">*</span></label>
        <MenuSelector v-model="menu_id" :restaurant-id="restaurant_id" :disabled="isSubmitting" />
      </div>

      <div class="form-field">
        <label>จำนวนเงิน (บาท) <span class="required">*</span></label>
        <InputNumber v-model="amount" :min="0.01" :max="10000" :step="0.5" class="p-fluid" :disabled="isSubmitting" />
        <small class="p-error">{{ errors.amount }}</small>
      </div>

      <div class="form-field">
        <label>หมวดหมู่ <span class="required">*</span></label>
        <Select v-model="category" :options="EXPENSE_CATEGORIES" optionLabel="label" optionValue="value" class="p-fluid" :disabled="isSubmitting" />
        <small class="p-error">{{ errors.category }}</small>
      </div>

      <div class="form-field">
        <label>วันที่ <span class="required">*</span></label>
        <DatePicker v-model="date" dateFormat="yy-mm-dd" class="p-fluid" :disabled="isSubmitting" />
        <small class="p-error">{{ errors.date }}</small>
      </div>

      <div class="form-field full-width">
        <label>หมายเหตุ</label>
        <Textarea v-model="note" :rows="3" class="p-fluid" :disabled="isSubmitting" />
        <small class="p-error">{{ errors.note }}</small>
      </div>
    </div>

    <div class="form-actions">
      <button type="button" class="p-button p-button-outlined" @click="emit('cancel')" :disabled="isSubmitting">ยกเลิก</button>
      <button type="submit" class="p-button" :disabled="isSubmitting">{{ isEditing ? 'บันทึก' : 'เพิ่มรายจ่าย' }}</button>
    </div>
  </form>
</template>

<style scoped>
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-field { display: flex; flex-direction: column; gap: 0.5rem; }
.full-width { grid-column: 1 / -1; }
.required { color: red; }
.form-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1rem; }
@media (max-width: 640px) { .form-grid { grid-template-columns: 1fr; } }
</style>
