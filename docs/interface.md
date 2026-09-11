# Shared interface — Module 2

The college sign-in layout is at `/accounts/login/`. Email input and continuation remain disabled until Module 3 provides authentication. No request is submitted and no account is created by the UI.

For local design review, open `/dev/ui/`. This separate GET-only preview is registered only with DEBUG enabled; the view also refuses production requests. It queries no users or research records. Its four navigation destinations are discovery, projects, communities, and a development component gallery. This navigation is a presentation scaffold for future authenticated views, not access to a real dashboard.

## Reusable pieces

- `templates/base.html`: document shell, stylesheet/script loading, skip link, content blocks.
- `templates/layouts/workspace.html`: workspace shell with responsive sidebar/top bar. Preview URLs and account text must be replaced by authorised application context when real routes arrive.
- `templates/components/`: brand, consistent line icons, Django messages, bound form fields, and reusable empty states.
- `static/css/base.css`: colour/spacing styles, controls, status messages, tables, project-card grid, authentication and workspace layouts.
- `static/js/ui.js`: mobile navigation, dismissible native details panels, Escape/focus handling, and clearly labelled feedback demonstration.

No external fonts, icon packages, analytics, framework, or image service is required. The text identity is replaceable, not an official university logo.

## Interaction boundaries

Navigation links, notification/profile disclosures, mobile navigation, and component feedback/reset operate now. Create Idea, discovery filters, and sign-in remain disabled with visible preview context. No fake achievements, users, unread counts, or project records are generated. The card gallery uses explicit layout samples. The five community destinations are labels at this stage, not implemented pages.

The form-field include renders Django bound widgets. Future forms should supply appropriate widget autocomplete and `aria-describedby` references to `<auto_id>_helptext` / `<auto_id>_error`, and `aria-invalid` for errors. No generic form submission interception has been introduced; actual save states must be wired to real server responses.

## Responsive and accessibility behaviour

Desktop uses a navy sidebar, compact white top bar, and content canvas. Navigation collapses at 760px; its button exposes expanded state. Project-card samples use three columns above 1150px, two at intermediate widths, and one at phone widths. Tables scroll inside a labelled focusable region. Focus outlines and skip navigation are visible; controls have labels, disabled states, and status messages. Reduced-motion preferences are respected.

Browser verification and limitations are recorded in `status.md`. No full accessibility audit is claimed.

Visual refinement: `static/css/refinement.css` layers the entrance and workspace polish over shared base controls. Discovery now uses clearly labelled template-only illustrative topic cards, not actual project records; all research actions remain pending their modules.
