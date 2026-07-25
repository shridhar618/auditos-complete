import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});
export type LoginFormValues = z.infer<typeof loginSchema>;

export const registerSchema = z.object({
  organization_name: z.string().min(2, "Organization name is too short"),
  full_name: z.string().min(2, "Enter your full name"),
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});
export type RegisterFormValues = z.infer<typeof registerSchema>;

export const createTransactionSchema = z.object({
  department_id: z.string().optional(),
  vendor_id: z.string().optional(),
  description: z.string().optional(),
  amount: z.coerce.number().positive("Amount must be greater than 0"),
  currency: z.string().length(3, "Use a 3-letter currency code").default("USD"),
  transaction_date: z.string().min(1, "Date is required"),
});
export type CreateTransactionFormValues = z.infer<typeof createTransactionSchema>;
