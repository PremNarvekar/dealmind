import * as React from "react"
import { cn } from "../../lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "success" | "warning" | "danger" | "outline"
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-[#0f172a] focus:ring-offset-2",
        {
          "border-transparent bg-[#0f172a] text-[#f8fafc]": variant === "default",
          "border-transparent bg-[#f0fdf4] text-[#16a34a]": variant === "success",
          "border-transparent bg-[#fffbeb] text-[#d97706]": variant === "warning",
          "border-transparent bg-[#fef2f2] text-[#dc2626]": variant === "danger",
          "text-[#0f172a] border border-[#e2e8f0]": variant === "outline",
        },
        className
      )}
      {...props}
    />
  )
}

export { Badge }
