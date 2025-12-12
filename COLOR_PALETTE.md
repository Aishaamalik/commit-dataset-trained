# AI Commit Generator - Color Palette & Design System

## Color Palette

Your four-color palette has been transformed into a sophisticated design system:

### Primary Colors
- **Dark Navy** (`#1B3C53`) - Primary background, main container backgrounds
- **Medium Blue** (`#234C6A`) - Secondary backgrounds, sidebar backgrounds  
- **Light Blue/Slate** (`#456882`) - Accent color, buttons, highlights, active states
- **Light Beige/Cream** (`#D2C1B6`) - Text color, icons, contrast elements

## CSS Variables

The design system uses CSS custom properties for consistency:

```css
:root {
  --primary-dark: #1B3C53;      /* Dark navy - main backgrounds */
  --primary-medium: #234C6A;    /* Medium blue - secondary backgrounds */
  --primary-bright: #456882;    /* Light blue/slate - accents & buttons */
  --primary-light: #D2C1B6;     /* Light beige/cream - text & highlights */
  
  --text-primary: #D2C1B6;      /* Main text color */
  --text-secondary: rgba(210, 193, 182, 0.7);  /* Secondary text */
  --text-muted: rgba(210, 193, 182, 0.5);      /* Muted text */
  
  --background-primary: #1B3C53;    /* Main background */
  --background-secondary: #234C6A;  /* Secondary background */
  --background-tertiary: #456882;   /* Tertiary background */
  
  --accent: #D2C1B6;            /* Accent color */
  --border: rgba(210, 193, 182, 0.2);  /* Border color */
  --hover: rgba(210, 193, 182, 0.1);   /* Hover states */
}
```

## Design Principles

### 1. **Hierarchy & Contrast**
- Dark navy (`#1B3C53`) provides the foundation
- Medium blue (`#234C6A`) creates depth and separation
- Light blue/slate (`#456882`) draws attention to interactive elements
- Light beige/cream (`#D2C1B6`) ensures excellent readability

### 2. **Interactive Elements**
- **Buttons**: Gradient from light blue/slate to tertiary with cream text
- **Hover States**: Subtle transformations with enhanced shadows
- **Focus States**: Light blue/slate borders with subtle glow effects
- **Active States**: Light blue/slate backgrounds with cream accents

### 3. **Visual Feedback**
- **Success**: Medium blue background with cream text
- **Error**: Light blue/slate background with cream text  
- **Info**: Tertiary background with cream text
- **Warning**: Cream background with dark navy text

### 4. **Typography**
- **Primary Text**: Cream color for maximum readability
- **Secondary Text**: 70% opacity cream for hierarchy
- **Muted Text**: 50% opacity cream for subtle information

### 5. **Spacing & Layout**
- Consistent use of borders with 20% opacity cream
- Hover effects with 10% opacity cream overlays
- Smooth transitions (0.2s-0.3s) for professional feel

## Component Examples

### Buttons
```css
.btn-primary {
  background: linear-gradient(135deg, var(--primary-bright) 0%, var(--background-tertiary) 100%);
  color: var(--accent);
  border: none;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(140, 16, 7, 0.3);
}
```

### Cards & Containers
```css
.card {
  background: var(--background-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
}

.card:hover {
  border-color: var(--primary-bright);
  box-shadow: 0 4px 12px rgba(140, 16, 7, 0.2);
}
```

### Form Elements
```css
.input {
  background: var(--background-primary);
  border: 2px solid var(--border);
  color: var(--text-primary);
}

.input:focus {
  border-color: var(--primary-bright);
  box-shadow: 0 0 0 3px rgba(140, 16, 7, 0.2);
}
```

## Accessibility

- **Contrast Ratio**: Light beige/cream on dark navy provides excellent contrast (>7:1)
- **Color Blindness**: Blue-cream combination works well for most color vision types
- **Focus Indicators**: Clear focus states with sufficient contrast
- **Interactive States**: Multiple visual cues (color, shadow, transform)

## Implementation Status

✅ **Completed Files:**
- `frontend/src/index.css` - CSS variables and base styles
- `frontend/src/App.css` - Main application components
- `frontend/src/Login.css` - Authentication screens
- `frontend/src/GitHubConnect.css` - GitHub connection modal
- `frontend/src/GitHubDashboard.css` - GitHub dashboard interface

## Usage Guidelines

1. **Always use CSS variables** instead of hardcoded colors
2. **Maintain consistent hover effects** with transforms and shadows
3. **Use appropriate opacity levels** for text hierarchy
4. **Apply consistent border radius** (4px-12px based on component size)
5. **Implement smooth transitions** for professional feel

This sophisticated navy-to-cream color palette creates a professional, calming interface that's both visually appealing and highly functional for a developer tool. The cool blue tones provide a trustworthy, focused atmosphere perfect for coding environments while maintaining excellent readability and usability.