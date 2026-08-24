export interface Budget {
  daily_budget: number;
}

export interface BudgetSummary {
  daily_budget: number;
  spent_today: number;
  remaining_today: number;
  is_over_budget: boolean;
}
