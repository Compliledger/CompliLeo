interface DecisionPillProps {
  ok: boolean;
  trueLabel?: string;
  falseLabel?: string;
}

export default function DecisionPill({
  ok,
  trueLabel = 'TRUE',
  falseLabel = 'FALSE',
}: DecisionPillProps) {
  return ok ? (
    <span className="pill-ok mono">
      <svg
        viewBox="0 0 20 20"
        fill="currentColor"
        className="h-3 w-3"
        aria-hidden
      >
        <path
          fillRule="evenodd"
          d="M16.704 5.29a1 1 0 010 1.42l-7.5 7.5a1 1 0 01-1.42 0l-3.5-3.5a1 1 0 111.42-1.42l2.79 2.79 6.79-6.79a1 1 0 011.42 0z"
          clipRule="evenodd"
        />
      </svg>
      {trueLabel}
    </span>
  ) : (
    <span className="pill-bad mono">
      <svg
        viewBox="0 0 20 20"
        fill="currentColor"
        className="h-3 w-3"
        aria-hidden
      >
        <path
          fillRule="evenodd"
          d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
          clipRule="evenodd"
        />
      </svg>
      {falseLabel}
    </span>
  );
}
