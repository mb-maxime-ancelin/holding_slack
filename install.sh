#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOLDING_SLACK_PY="$SCRIPT_DIR/holding_slack.py"
SNIPPET_FILE="$HOME/.holding_slack.sh"
GUARD_START="# >>> holding_slack >>>"
GUARD_END="# <<< holding_slack <<<"

bold()  { printf '\033[1m%s\033[0m\n' "$*"; }
info()  { printf '  %s\n' "$*"; }
warn()  { printf '\033[33m  %s\033[0m\n' "$*"; }
die()   { printf '\033[31merror: %s\033[0m\n' "$*" >&2; exit 1; }

[ -f "$HOLDING_SLACK_PY" ] || die "holding_slack.py not found next to install.sh ($HOLDING_SLACK_PY)"

bold "holding_slack installer"
info "script:  $HOLDING_SLACK_PY"
info "snippet: $SNIPPET_FILE"
echo

OS="$(uname -s)"
case "$OS" in
    Linux)  info "os:      Linux" ;;
    Darwin) info "os:      macOS" ;;
    *)      warn "os:      $OS (untested, continuing)" ;;
esac

# --- shell detection ---------------------------------------------------------
default_shell="$(basename "${SHELL:-bash}")"
case "$default_shell" in
    zsh|bash) ;;
    *) default_shell="bash" ;;
esac

printf "Install for which shell? [b]ash / [z]sh / [both] (default: %s): " "$default_shell"
read -r ans
ans="${ans:-$default_shell}"
case "$ans" in
    b|bash)       shells=("bash") ;;
    z|zsh)        shells=("zsh") ;;
    both)         shells=("bash" "zsh") ;;
    *)            die "unknown shell choice: $ans" ;;
esac

rc_files=()
for sh in "${shells[@]}"; do
    case "$sh" in
        bash)
            if [ "$OS" = "Darwin" ] && [ ! -f "$HOME/.bashrc" ] && [ -f "$HOME/.bash_profile" ]; then
                rc_files+=("$HOME/.bash_profile")
            else
                rc_files+=("$HOME/.bashrc")
            fi
            ;;
        zsh)  rc_files+=("$HOME/.zshrc") ;;
    esac
done

# --- terminal detection ------------------------------------------------------
detect_terminal() {
    if [ -n "${WEZTERM_EXECUTABLE:-}" ] || [ "${TERM_PROGRAM:-}" = "WezTerm" ]; then
        echo "wezterm"
    elif [ "${TERM_PROGRAM:-}" = "iTerm.app" ]; then
        echo "iterm"
    elif [ "${TERM_PROGRAM:-}" = "WarpTerminal" ]; then
        echo "warp"
    elif [ -n "${KITTY_WINDOW_ID:-}" ]; then
        echo "kitty"
    elif [ -n "${GNOME_TERMINAL_SCREEN:-}" ]; then
        echo "gnome-terminal"
    elif [ -n "${ALACRITTY_LOG:-}" ] || [ "${TERM:-}" = "alacritty" ]; then
        echo "alacritty"
    elif [ "${TERM_PROGRAM:-}" = "Apple_Terminal" ]; then
        echo "apple-terminal"
    else
        echo "generic"
    fi
}

terminal="$(detect_terminal)"
echo
info "detected terminal: $terminal"
printf "Use this? [Y]es / [n]o (pick manually) / [s]kip (no title support): "
read -r ans
case "${ans:-y}" in
    y|Y|yes) ;;
    s|skip)  terminal="skip" ;;
    *)
        echo
        echo "  1) wezterm         (wezterm cli, fallback ANSI)"
        echo "  2) iterm           (ANSI)"
        echo "  3) warp            (ANSI)"
        echo "  4) kitty           (kitty @, fallback ANSI)"
        echo "  5) gnome-terminal  (ANSI)"
        echo "  6) alacritty       (ANSI)"
        echo "  7) apple-terminal  (ANSI)"
        echo "  8) generic         (ANSI)"
        echo "  9) skip            (no title)"
        printf "Pick 1-9: "
        read -r pick
        case "$pick" in
            1) terminal="wezterm" ;;
            2) terminal="iterm" ;;
            3) terminal="warp" ;;
            4) terminal="kitty" ;;
            5) terminal="gnome-terminal" ;;
            6) terminal="alacritty" ;;
            7) terminal="apple-terminal" ;;
            8) terminal="generic" ;;
            9) terminal="skip" ;;
            *) die "invalid pick: $pick" ;;
        esac
        ;;
esac
info "using terminal: $terminal"

# --- emit set_title body -----------------------------------------------------
set_title_body() {
    case "$terminal" in
        wezterm)
            cat <<'EOF'
set_title() {
  if command -v wezterm >/dev/null 2>&1; then
    wezterm cli set-tab-title "$*"
  else
    printf '\033]0;%s\007' "$*"
  fi
}
EOF
            ;;
        kitty)
            cat <<'EOF'
set_title() {
  if command -v kitty >/dev/null 2>&1; then
    kitty @ set-tab-title "$*" 2>/dev/null || printf '\033]0;%s\007' "$*"
  else
    printf '\033]0;%s\007' "$*"
  fi
}
EOF
            ;;
        skip)
            cat <<'EOF'
set_title() { :; }
EOF
            ;;
        *)
            cat <<'EOF'
set_title() { printf '\033]0;%s\007' "$*"; }
EOF
            ;;
    esac
}

# --- generate snippet --------------------------------------------------------
if [ -f "$SNIPPET_FILE" ]; then
    cp "$SNIPPET_FILE" "$SNIPPET_FILE.bak"
    warn "backed up existing snippet to $SNIPPET_FILE.bak"
fi

{
    echo "# Managed by holding_slack install.sh — regenerate with $SCRIPT_DIR/install.sh"
    echo "# Terminal: $terminal  |  Generated for: ${shells[*]}"
    echo
    echo "HOLDING_SLACK=\"$HOLDING_SLACK_PY\""
    echo 'HOLDING_SLACK_DIR="$(dirname "$HOLDING_SLACK")"'
    echo
    set_title_body
    echo 't_() { set_title "$*"; }'
    echo
    echo 'holding_slack() { (cd "$HOLDING_SLACK_DIR" && "$HOLDING_SLACK" "$1"); }'
    echo
    echo 'st_testing() { t_ "🔥 testing"; holding_slack testing; }'
    echo 'st_morning() { t_ "☀️ morning"; holding_slack morning; }'
    echo 'st_lunch()   { t_ "🍔 lunch";   holding_slack lunch;   }'
    echo 'st_back()    { t_ "🌇 back";    holding_slack back;    }'
    echo 'st_closing() { t_ "🌙 closing"; holding_slack closing; }'
} > "$SNIPPET_FILE"

info "wrote $SNIPPET_FILE"

# --- wire into rc files ------------------------------------------------------
for rc in "${rc_files[@]}"; do
    if [ -f "$rc" ] && grep -Fq "$GUARD_START" "$rc"; then
        info "rc already wired: $rc (skipped)"
        continue
    fi
    {
        echo ""
        echo "$GUARD_START"
        echo '[ -f "$HOME/.holding_slack.sh" ] && . "$HOME/.holding_slack.sh"'
        echo "$GUARD_END"
    } >> "$rc"
    info "updated $rc"
done

echo
bold "done."
info "available: st_morning  st_lunch  st_back  st_closing  st_testing"
info "activate now: source ${rc_files[0]}"
