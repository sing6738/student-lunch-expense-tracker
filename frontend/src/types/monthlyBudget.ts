export interface MonthlyBudget {
  id: number;
  year: number;
  month: number;
  monthly_income: number;
  fixed_internet: number;
  fixed_phone: number;
  fixed_water: number;
  fixed_electric: number;
  fixed_rent: number;
  fixed_other: number;
  fixed_other_note?: string;
  total_fixed: number;
  remaining_for_variable: number;
}

export interface MonthlyBudgetSummary {
  total_income: number;
  total_fixed: number;
  remaining_for_variable: number;
  total_spent_variable: number;
  remaining_balance: number;
}
