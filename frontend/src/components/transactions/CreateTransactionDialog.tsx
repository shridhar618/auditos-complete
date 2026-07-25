import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Plus } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { NativeSelect } from "@/components/ui/native-select";
import { useCreateTransaction, useDepartments, useVendors } from "@/hooks/useTransactions";
import { type CreateTransactionFormValues, createTransactionSchema } from "@/lib/validation";

export function CreateTransactionDialog() {
  const [open, setOpen] = useState(false);
  const { data: departments } = useDepartments();
  const { data: vendors } = useVendors();
  const createTransaction = useCreateTransaction();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateTransactionFormValues>({
    resolver: zodResolver(createTransactionSchema),
    defaultValues: { currency: "USD", transaction_date: new Date().toISOString().slice(0, 10) },
  });

  const onSubmit = async (values: CreateTransactionFormValues) => {
    await createTransaction.mutateAsync({
      department_id: values.department_id || undefined,
      vendor_id: values.vendor_id || undefined,
      description: values.description || undefined,
      amount: values.amount,
      currency: values.currency.toUpperCase(),
      transaction_date: values.transaction_date,
    });
    reset();
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4" />
          New Transaction
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Record a transaction</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="amount">Amount</Label>
            <div className="flex gap-2">
              <Input id="amount" type="number" step="0.01" placeholder="0.00" {...register("amount")} />
              <Input className="w-20" placeholder="USD" maxLength={3} {...register("currency")} />
            </div>
            {errors.amount && <p className="text-xs text-destructive">{errors.amount.message}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="transaction_date">Transaction date</Label>
            <Input id="transaction_date" type="date" {...register("transaction_date")} />
            {errors.transaction_date && <p className="text-xs text-destructive">{errors.transaction_date.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="department_id">Department</Label>
              <NativeSelect id="department_id" {...register("department_id")}>
                <option value="">Unassigned</option>
                {departments?.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </NativeSelect>
            </div>
            <div className="space-y-2">
              <Label htmlFor="vendor_id">Vendor</Label>
              <NativeSelect id="vendor_id" {...register("vendor_id")}>
                <option value="">Unassigned</option>
                {vendors?.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name}
                  </option>
                ))}
              </NativeSelect>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input id="description" placeholder="Optional note about this transaction" {...register("description")} />
          </div>

          {createTransaction.isError && (
            <p className="text-sm text-destructive">Couldn't save this transaction. Please try again.</p>
          )}

          <Button type="submit" className="w-full" disabled={createTransaction.isPending}>
            {createTransaction.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Save transaction
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
