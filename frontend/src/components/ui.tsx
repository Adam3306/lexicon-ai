"use client";

import * as React from "react";

export function clsx(...parts: Array<string | undefined | false | null>) {
  return parts.filter(Boolean).join(" ");
}

export function Button(
  props: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" }
) {
  const { className, variant = "primary", ...rest } = props;
  const base =
    "inline-flex items-center justify-center rounded-lg px-3 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed";
  const styles =
    variant === "primary"
      ? "bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
      : "border border-zinc-200 bg-white text-zinc-900 hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-100 dark:hover:bg-zinc-900";
  return <button className={clsx(base, styles, className)} {...rest} />;
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  const { className, ...rest } = props;
  return (
    <input
      className={clsx(
        "w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none ring-0 placeholder:text-zinc-400 focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-950 dark:placeholder:text-zinc-500 dark:focus:border-zinc-600",
        className
      )}
      {...rest}
    />
  );
}

export function Textarea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const { className, ...rest } = props;
  return (
    <textarea
      className={clsx(
        "w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none placeholder:text-zinc-400 focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-950 dark:placeholder:text-zinc-500 dark:focus:border-zinc-600",
        className
      )}
      {...rest}
    />
  );
}

export function Card(props: React.HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props;
  return (
    <div
      className={clsx(
        "rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-950",
        className
      )}
      {...rest}
    />
  );
}

export function Label(props: React.LabelHTMLAttributes<HTMLLabelElement>) {
  const { className, ...rest } = props;
  return <label className={clsx("text-sm font-medium text-zinc-800 dark:text-zinc-200", className)} {...rest} />;
}

export function FieldHint(props: React.HTMLAttributes<HTMLParagraphElement>) {
  const { className, ...rest } = props;
  return <p className={clsx("text-xs text-zinc-500 dark:text-zinc-400", className)} {...rest} />;
}

