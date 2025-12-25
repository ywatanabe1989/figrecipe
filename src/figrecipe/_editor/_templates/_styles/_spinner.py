#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spinner/loading indicator styles for the figure editor."""

STYLES_SPINNER = """
/* ==================== SPINNER/LOADING OVERLAY ==================== */

/* Spinner overlay container */
.spinner-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    display: none;
    justify-content: center;
    align-items: center;
    z-index: 10000;
    backdrop-filter: blur(2px);
}

/* Show spinner when body has loading class */
body.loading .spinner-overlay {
    display: flex;
}

/* Spinner container */
.spinner-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}

/* The spinner itself */
.spinner {
    width: 48px;
    height: 48px;
    border: 4px solid rgba(255, 255, 255, 0.2);
    border-top-color: var(--accent-color, #2563eb);
    border-radius: 50%;
    animation: spinner-rotate 0.8s linear infinite;
}

/* Spinner animation */
@keyframes spinner-rotate {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

/* Loading text */
.spinner-text {
    color: white;
    font-size: 14px;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

/* Dark mode adjustments */
[data-theme="dark"] .spinner-overlay {
    background: rgba(0, 0, 0, 0.6);
}

[data-theme="dark"] .spinner {
    border-color: rgba(255, 255, 255, 0.1);
    border-top-color: var(--accent-color, #3b82f6);
}

/* Mini spinner for inline use */
.spinner-mini {
    width: 16px;
    height: 16px;
    border-width: 2px;
    display: inline-block;
    vertical-align: middle;
    margin-right: 6px;
}

/* Button loading state */
button.btn-loading {
    position: relative;
    color: transparent !important;
}

button.btn-loading::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 16px;
    height: 16px;
    margin: -8px 0 0 -8px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spinner-rotate 0.8s linear infinite;
}

/* Loading state - keep existing behavior but remove pointer events */
body.loading {
    pointer-events: none;
}

/* Keep controls interactive even when loading */
body.loading .spinner-overlay {
    pointer-events: auto;
}
"""

__all__ = ["STYLES_SPINNER"]

# EOF
