# -*- coding: utf-8 -*-
"""Unica Studio — property enhancement portfolio site.

Thin Flask server that renders a single, content-driven page from
data/portfolio.json + the CONTENT dict below. Runs locally during
development and deploys to Railway (gunicorn) without changes.
"""
import json
import os

from flask import Flask, render_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


def load_portfolio():
    path = os.path.join(BASE_DIR, "data", "portfolio.json")
    if not os.path.exists(path):
        return {"projects": []}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Site content (Hebrew). Edit copy here — the template stays untouched.
# Items marked PLACEHOLDER should be replaced with the studio's real details.
# ---------------------------------------------------------------------------
CONTENT = {
    "brand": "UNICA",
    "brand_he": "יוניקה",
    "tagline": "סטודיו לעיצוב פנים והשבחת נכסים",
    "owner": "סברינה בקלו",
    "photographer": "ניב נבון",
    "hours": ["ראשון–חמישי · 9:30–17:00", "שישי · 9:30–12:30"],
    "nav": [
        {"label": "הסטודיו", "href": "#studio"},
        {"label": "שירותים", "href": "#services"},
        {"label": "תהליך", "href": "#process"},
        {"label": "עבודות", "href": "#work"},
        {"label": "צור קשר", "href": "#contact"},
    ],
    "hero": {
        "kicker": "סטודיו להשבחת נכסים",
        "title_lines": ["כל נכס מחביא בתוכו ערך.", "אנחנו חושפים אותו."],
        "sub": "יוניקה מלווה בעלי דירות, משקיעים ומתווכים בתהליך השבחה מלא — "
               "מאבחון הפוטנציאל, דרך תכנון ועיצוב, ועד תוצאה שמדברת בעד עצמה.",
        "cta_primary": {"label": "לשיחת ייעוץ", "href": "#contact"},
        "cta_secondary": {"label": "לעבודות שלנו", "href": "#work"},
    },
    "statement": "השבחה היא לא רק שיפוץ. זו הדרך להציג נכס במיטבו — "
                 "כך שהקונה הנכון רואה בית, והערך עולה בהתאם.",
    "studio": {
        "label": "הכרות",
        "title": "פרטים קטנים. הבדל גדול.",
        "intro": "נעים להכיר — סברינה בקלו, מייסדת יוניקה.",
        "paragraphs": [
            "עם עין חדה לפרטים, חשיבה מסחרית והיכרות עמוקה עם מה שגורם לנכס "
            "להימכר — סברינה לוקחת כל פרויקט מהבנה של הפוטנציאל הטמון בקירות, "
            "ועד לנכס שקשה לעבור לידו.",
            "אנחנו מלווים את התהליך מקצה לקצה — תכנון, עיצוב, ביצוע וסטיילינג — "
            "בליווי צמוד, בזמן ובתקציב. התוצאה: חללים שנמכרים מהר יותר, "
            "ובמחיר טוב יותר.",
        ],
        "portrait": "img/team/sabrina.jpg",
        "portrait_alt": "סברינה בקלו, מייסדת יוניקה",
    },
    "services": {
        "label": "שירותים",
        "title": "מה אנחנו עושים",
        "items": [
            {"n": "01", "title": "ייעוץ ואבחון",
             "text": "הערכת הפוטנציאל הכלכלי של הנכס ובניית אסטרטגיית השבחה מדויקת."},
            {"n": "02", "title": "תכנון ועיצוב",
             "text": "קונספט עיצובי, תכנון חללים ובחירת חומרים וגימורים."},
            {"n": "03", "title": "שיפוץ וניהול",
             "text": "ביצוע מלא בליווי צמוד מול בעלי המקצוע — בזמן ובתקציב."},
            {"n": "04", "title": "סטיילינג והשמה",
             "text": "העיצוב הסופי שמכניס חיים לחלל ומספר את הסיפור הנכון."},
            {"n": "05", "title": "צילום ושיווק",
             "text": "צילום מקצועי שמציג את הנכס במיטבו וממקסם את החשיפה."},
        ],
    },
    "process": {
        "label": "התהליך",
        "title": "מהפוטנציאל לתוצאה",
        "steps": [
            {"n": "01", "title": "פגישה ואבחון",
             "text": "מכירים את הנכס, מבינים את המטרה ומזהים את ההזדמנות."},
            {"n": "02", "title": "תכנון ועיצוב",
             "text": "מגבשים קונספט, חומרים ותקציב — תמונה ברורה לפני שמתחילים."},
            {"n": "03", "title": "ביצוע",
             "text": "מנהלים את כל בעלי המקצוע ומבצעים עד הפרט האחרון."},
            {"n": "04", "title": "תוצאה ומכירה",
             "text": "מעצבים, מצלמים ומגישים נכס מוכן שמדבר בעד עצמו."},
        ],
    },
    "work": {
        "label": "עבודות נבחרות",
        "title": "פרויקטים אחרונים",
        "sub": "מבחר נכסים שעברו תחת ידינו טרנספורמציה מלאה.",
        "project_kicker": "השבחה ועיצוב",
    },
    "ba": {
        "label": "לפני / אחרי",
        "title": "רואים את ההפרש",
        "sub": "גררו את הידית כדי לראות את הטרנספורמציה.",
        "after": "img/ba/after.webp",
        "after_jpg": "img/ba/after.jpg",
        "before": "img/ba/before.webp",
        "before_jpg": "img/ba/before.jpg",
        # PLACEHOLDER — replace with a real "before" photo of the property.
        "note": "תמונת ״לפני״ להמחשה — תוחלף בתמונות אמיתיות מהפרויקטים.",
        "tag_before": "לפני",
        "tag_after": "אחרי",
    },
    "values": {
        "label": "למה יוניקה",
        "title": "מוציאים את המיטב מכל נכס",
        "items": [
            {"title": "מקסום ערך", "text": "כל החלטה מכוונת להגדלת השווי של הנכס."},
            {"title": "דיוק מוקפד", "text": "ירידה לפרטים הקטנים שעושים את ההבדל."},
            {"title": "ראש שקט", "text": "ליווי מלא מקצה לקצה — בזמן ובתקציב."},
            {"title": "תוצאה מדויקת", "text": "נכס מוגמר שמדבר בעד עצמו, ומוכר."},
        ],
        "closing": "השבחה היא לא רק עיצוב — היא דרך חכמה ליצור ערך.",
    },
    "quote": {
        "text": "סברינה לקחה דירה ישנה והפכה אותה לנכס שנמכר תוך שבועיים, "
                "הרבה מעל המחיר שציפינו לו.",
        "author": "PLACEHOLDER — שם לקוח/ה",
    },
    # Which renovated apartment photograph to use as the background of each
    # non-work panel. {project: index into portfolio.projects, img: index into that
    # project's images[]}. Curated to use the "wow" landscape shots, never the
    # staging/unfinished frames.
    "panel_bg": {
        "hero":      {"project": 4, "img": 5},   # hashalom-31 — Simplicity sofa
        "statement": {"project": 0, "img": 1},   # matudela-6 — wide brush-stroke interior
        "studio":    {"project": 1, "img": 5},   # avraham-avinu-24 — line-art sofa
        "services":  {"project": 3, "img": 2},   # david-hamelech-25 — wood slats + leaf art (interior)
        "process":   {"project": 4, "img": 6},   # hashalom-31 — wide open-plan view
        "values":    {"project": 1, "img": 4},   # avraham-avinu-24 — wicker pendant
        "quote":     {"project": 0, "img": 3},   # matudela-6 — yellow chair + fluted
        "contact":   {"project": 5, "img": 9},   # giora-24 — wood kitchen + zebra blinds
    },
    "contact": {
        "label": "צור קשר",
        "title": "מוכנים להשביח את הנכס שלכם?",
        "sub": "ספרו לנו על הנכס — ונחזור אליכם עם הערכת פוטנציאל ראשונית.",
        # PLACEHOLDER — replace with the studio's real details.
        "phone_display": "050-000-0000",
        "phone": "+972500000000",
        "whatsapp": "972500000000",
        "whatsapp_msg": "היי, אשמח לשמוע על שירותי השבחת הנכסים של יוניקה",
        "email": "Unica.Studio.Sabrina@gmail.com",
        "instagram_handle": "unica.studio",
        "instagram_url": "https://instagram.com/unica.studio",
    },
}


@app.context_processor
def inject_globals():
    import datetime
    return {
        "c": CONTENT,
        "portfolio": load_portfolio(),
        "year": datetime.date.today().year,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/healthz")
def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    # Reloader watches the whole conda env on Windows and restarts mid-request,
    # so keep it off — restart manually when iterating on Python code.
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
