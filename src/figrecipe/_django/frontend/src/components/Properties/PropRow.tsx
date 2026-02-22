/** Single property row — label + editable input, color picker, checkbox, select. */

export function PropRow({
  label,
  value,
  editable = false,
  type = "text",
  onChange,
  options,
}: {
  label: string;
  value: string | number | boolean;
  editable?: boolean;
  type?: "text" | "number" | "color" | "checkbox" | "select";
  onChange?: (val: string | number | boolean) => void;
  options?: { label: string; value: string }[];
}) {
  if (!editable) {
    return (
      <div className="property-row">
        <div className="property-group">
          <span className="property-label">{label}</span>
          <span
            className="property-input"
            style={{ border: "none", padding: 0, background: "none" }}
          >
            {String(value)}
          </span>
        </div>
      </div>
    );
  }

  if (type === "checkbox") {
    return (
      <div className="property-row">
        <label className="property-checkbox">
          <input
            type="checkbox"
            checked={Boolean(value)}
            onChange={(e) => onChange?.(e.target.checked)}
          />
          <span>{label}</span>
        </label>
      </div>
    );
  }

  if (type === "color") {
    return (
      <div className="property-row">
        <div className="property-group">
          <span className="property-label">{label}</span>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <input
              className="property-color"
              type="color"
              value={String(value)}
              onChange={(e) => onChange?.(e.target.value)}
            />
            <span style={{ fontSize: 11, color: "var(--vis-text-muted)" }}>
              {String(value)}
            </span>
          </div>
        </div>
      </div>
    );
  }

  if (type === "select" && options) {
    return (
      <div className="property-row">
        <div className="property-group">
          <span className="property-label">{label}</span>
          <select
            className="property-select"
            value={String(value)}
            onChange={(e) => onChange?.(e.target.value)}
          >
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    );
  }

  return (
    <div className="property-row">
      <div className="property-group">
        <span className="property-label">{label}</span>
        <input
          className="property-input"
          type={type}
          value={String(value)}
          onChange={(e) =>
            onChange?.(
              type === "number" ? Number(e.target.value) : e.target.value,
            )
          }
        />
      </div>
    </div>
  );
}
