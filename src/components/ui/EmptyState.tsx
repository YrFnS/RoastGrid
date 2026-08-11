"use client"

import { FileText, type LucideIcon } from 'lucide-react'
import { Button } from './button'
import { cn } from '@/lib/utils'

export type EmptyStateIconName = 'file-text'

const namedIcons: Record<EmptyStateIconName, LucideIcon> = {
  'file-text': FileText,
}

interface EmptyStateProps {
  icon?: LucideIcon
  iconName?: EmptyStateIconName
  title: string
  description?: string
  action?: { label: string; onClick: () => void }
  className?: string
}

export function EmptyState({
  icon,
  iconName,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  const Icon = iconName ? namedIcons[iconName] : icon

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-xl p-8 bg-surface-container-lowest text-center',
        className
      )}
    >
      {Icon && (
        <Icon className="w-12 h-12 text-on-surface-variant mb-4" />
      )}
      <h3 className="text-body-lg font-medium text-on-surface mb-1">
        {title}
      </h3>
      {description && (
        <p className="text-body-sm text-on-surface-variant max-w-xs">
          {description}
        </p>
      )}
      {action && (
        <Button
          variant="default"
          size="sm"
          className="mt-4"
          onClick={action.onClick}
        >
          {action.label}
        </Button>
      )}
    </div>
  )
}
