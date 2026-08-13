import * as React from "react"
import { cn } from "../../lib/utils"
import { AlertCircle, AlertTriangle, CheckCircle2 } from "lucide-react"

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "danger" | "success" | "warning"
  title: string
  description?: string
}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant = "default", title, description, ...props }, ref) => {
    return (
      <div
        ref={ref}
        role="alert"
        className={cn(
          "relative w-full rounded-lg border p-4 [&>svg]:absolute [&>svg]:text-foreground [&>svg]:left-4 [&>svg]:top-4 [&>svg+div]:translate-y-[-3px] [&:has(svg)]:pl-11",
          {
            "bg-white text-[#0f172a] border-[#e2e8f0]": variant === "default",
            "bg-[#fef2f2] text-[#dc2626] border-[#fecaca] [&>svg]:text-[#dc2626]": variant === "danger",
            "bg-[#f0fdf4] text-[#16a34a] border-[#bbf7d0] [&>svg]:text-[#16a34a]": variant === "success",
            "bg-[#fffbeb] text-[#d97706] border-[#fde68a] [&>svg]:text-[#d97706]": variant === "warning",
          },
          className
        )}
        {...props}
      >
        {variant === "danger" && <AlertCircle className="h-5 w-5" />}
        {variant === "success" && <CheckCircle2 className="h-5 w-5" />}
        {variant === "warning" && <AlertTriangle className="h-5 w-5" />}
        {variant === "default" && <AlertCircle className="h-5 w-5 text-[#64748b]" />}
        
        <h5 className="mb-1 font-medium leading-none tracking-tight">{title}</h5>
        {description && (
          <div className="text-sm opacity-90">
            {description}
          </div>
        )}
      </div>
    )
  }
)
Alert.displayName = "Alert"

export { Alert }
