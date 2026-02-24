/** Ribbon button — icon above label, vis_app .ribbon-btn pattern. */

interface Props {
  icon: string;
  label: string;
  onClick?: () => void;
  active?: boolean;
  disabled?: boolean;
  title?: string;
}

export function RibbonButton({
  icon,
  label,
  onClick,
  active,
  disabled,
  title,
}: Props) {
  return (
    <button
      className={`ribbon-btn${active ? " ribbon-btn--active" : ""}`}
      onClick={onClick}
      disabled={disabled}
      title={title ?? label}
      type="button"
    >
      <i className={icon} />
      <span>{label}</span>
    </button>
  );
}
