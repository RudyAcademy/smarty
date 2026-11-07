# Continue Smarty at C:\TowerHill\Smarty

You already have a Windows build at C:\TowerHill\Smarty. It runs, but the catalog is empty because the seed was never on that machine. Do not look for a zip, a handoff folder, or any other file. Do not ask for another upload. This message is the whole assignment. The three JSON documents are copied in full at the bottom.

Keep the Windows app you built. Do not replace it with a different project. Load this catalog into it. Show all 69 records as unreviewed, with blank notes and no approval. Do not invent ideas, URLs, scores, or dates.

This is the Tower Hill business-ideas app named Smarty. It is not an older Sparky camera or student-desk project, and it is not Learning Dragon or Professor. Do not open those codebases.

## Answers

1. The seed is the JSON in sections A, B, and C below. 59 ideas, 10 weekly performance records, 10 categories. Import those records. There is no separate file to find.

2. An earlier Linux prototype of this same app exists. Its Python package is named sparky. On Linux, python3 -m pytest -q reported 57 passed. That was not a Windows test. Do not throw away C:\TowerHill\Smarty. Keep your Windows build and make it behave like this: notes survive import and restart, rejection is recoverable, citations stay unchecked, layout is left tiles, right list, center detail.

3. The shared-folder path is not verified on the laptops. Until Rudy checks the real PC, configure:
   - Local data: C:\TowerHill\Grok-Bot-data\business-ideas\
   - Shared root: T:\TowerHill\Sparky\
   - Installers: T:\TowerHill\Sparky\Installers
   - Shared data: T:\TowerHill\Sparky\Data
   Do not hardcode a UNC path. A historical guess that T: might be \\192.168.2.100\Arhiva was never verified. Do not publish to the share. The folder name Sparky is legacy storage. Do not rename those folders because the app is called Smarty.

4. No device labels were chosen. Do not invent Rudy-Laptop or Lumi-Laptop. Each PC keeps its own device id. Leave the label blank until that person types one. Until then, show the device id.

5. For the five ideas with no URL, keep each record's own summary, advice, and missing_source_note from section B. All five use this missing_source_note: "Exact URL unavailable in weekly review; recover original record rather than invent citation." Also keep the specific wording already in those records (Pillar OS, Rogers-Feller, ClassDojo/Edutopia). Do not add a URL. A generic note alone is not enough.

6. Add an in-app Import batch action before this counts as done. A command-line import may remain, but Rudy and Lumi need the button. Use it to load sections A, B, and C if they are not already bundled.

7. Wire catalog refresh into startup now. Every launch tries the share with a short timeout, then opens the local copy if T: is missing. Do not freeze on a dead drive. Do not create T:\TowerHill\Sparky\Data if that folder is not already there. Do not announce success after a failed check.

8. A versioned zip plus a PowerShell script is enough. Write latest.json only after the zip hash matches. Do not build an MSI. Do not call the script a tested installer until you have run it on Windows.

9. Rudy or Lumi copy a release onto the Installers share by hand, after they confirm the T: mapping. Do not automate that copy.

10. The 7 content tiles and 3 status views are complete. Do not add a second Parent engagement tile. Statuses are unreviewed, kept, parked, and rejected. Rejection is recoverable and must not delete notes. Kept files the record in Rudy's collection and does not approve outreach, a development change, or spending. One record can appear in several content tiles and still have one id, one note, and one status.

## What the window must do

Left: category tiles. Right: chronological list for the selected tile. Center: the selected record. Center top about two thirds is the summary and practical advice. Center bottom about one third is the status controls and editable notes. Resizable. Usable at about 1366x768 and 1280x800. Do not swap center and right.

Received dates are the period 31 Oct 2026 through 7 Nov 2026, not a discovery clock. Do not show 7 Nov 2026 as the discovery time of every item. Newest first by default, with oldest first available. Ties use title, then id, and the screen says the original order inside that period is unknown.

Weekly performance records are dated notes, not scores. Professor stays a partial document check: v61 published, later geometry work unpublished and not release-ready. Do not soften that.

Bot implementation advice is labeled bot suggestion, not source evidence. Practical steps may be edited. Those edits are user data. A later import must not erase notes, status, or edited steps. Opening a card must not silently save the draft. Imported user_state must not pre-approve anything.

Citations stay unchecked. Copying a link is fine. Smarty must not message anyone.

Browse works offline with no AI API and no credits. First launch with no cache uses the JSON below.

Sync, when you implement it, must not use a live SQLite file on the share. Field edits are an append-only log. Two offline edits of the same field from the same base both stay until a person resolves them. A stale copy must not drop a rejection or a note. If the share is read-only or missing, keep the local edits.

## What to do now

1. Parse sections A, B, and C.
2. Confirm 59 ideas, 10 performance records, 10 categories, all unreviewed, notes blank, approval null.
3. Bundle that catalog into C:\TowerHill\Smarty so a cold start shows it with no extra file.
4. Add Import batch if it is not already there.
5. Run the app and your tests. Report pass/fail counts, the exact commands, and whether you ran them on Windows. If T: cannot be reached, say the app opened on the local copy. Do not claim the NAS was tested.

## A. categories.json

```json
{
  "categories": [
    {
      "id": "category-1",
      "label": "Weekly bots performance",
      "kind": "content_category",
      "status_filter": null
    },
    {
      "id": "category-2",
      "label": "Growth and enrolment",
      "kind": "content_category",
      "status_filter": null
    },
    {
      "id": "category-3",
      "label": "New audiences and channels",
      "kind": "content_category",
      "status_filter": null
    },
    {
      "id": "category-4",
      "label": "Parent engagement and retention",
      "kind": "content_category",
      "status_filter": null
    },
    {
      "id": "category-5",
      "label": "Teaching–Professor ideas",
      "kind": "content_category",
      "status_filter": null
    },
    {
      "id": "category-6",
      "label": "Learning Dragon ideas",
      "kind": "content_category",
      "status_filter": null
    },
    {
      "id": "category-7",
      "label": "Miscellaneous",
      "kind": "content_category",
      "status_filter": null
    },
    {
      "id": "category-8",
      "label": "Rudy's collection",
      "kind": "status_view",
      "status_filter": "kept"
    },
    {
      "id": "category-9",
      "label": "Park it for later",
      "kind": "status_view",
      "status_filter": "parked"
    },
    {
      "id": "category-10",
      "label": "Rejected (recoverable)",
      "kind": "status_view",
      "status_filter": "rejected"
    }
  ],
  "allowed_statuses": [
    "unreviewed",
    "kept",
    "parked",
    "rejected"
  ],
  "notes": "Single Parent engagement category; mutually exclusive statuses. Rejection recoverable, never physical delete; Teaching and Learning Dragon overlap permitted."
}
```

## B. ideas.json

```json
{
  "metadata": {
    "schema_version": 1,
    "prepared_on": "2026-11-07",
    "timezone": "America/Toronto",
    "provenance": "Supplied parent conversation; no web research",
    "chronology_note": "Period-only received dates: display Oct 31–Nov 7, 2026; original discovery dates unknown. Title/ID tie-break is not discovery order.",
    "privacy_note": "No private child/parent contacts, credentials, invented notes or approvals."
  },
  "ideas": [
    {
      "id": "sparky-idea-progress-report-decoder",
      "kind": "idea",
      "title": "Progress Report Decoder",
      "categories": [
        "Growth and enrolment"
      ],
      "originating_bots": [
        "Steve",
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Progress Report Decoder: Offer a free report-card discussion, possibly a PA-day workshop.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Offer a free report-card discussion, possibly a PA-day workshop."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.ontario.ca/page/student-assessment-evaluations-and-report-cards",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Offer a free report-card discussion, possibly a PA-day workshop.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        },
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Offer a free report-card discussion, possibly a PA-day workshop.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-holiday-gifts",
      "kind": "idea",
      "title": "Holiday learning gifts",
      "categories": [
        "Growth and enrolment"
      ],
      "originating_bots": [
        "Mark",
        "Steve"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Holiday learning gifts: Explore prepaid tutoring gifts for relatives, with Christmas and Lunar New Year variants.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Explore prepaid tutoring gifts for relatives, with Christmas and Lunar New Year variants."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.learninghive.ca/shop/p/the-gift-of-learning-the-perfect-gift-for-every-child",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Explore prepaid tutoring gifts for relatives, with Christmas and Lunar New Year variants.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        },
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Explore prepaid tutoring gifts for relatives, with Christmas and Lunar New Year variants.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-employer-partnerships",
      "kind": "idea",
      "title": "Employer-family partnerships",
      "categories": [
        "Growth and enrolment"
      ],
      "originating_bots": [
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Employer-family partnerships: Pilot a tutoring benefit with one nearby employer.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Pilot a tutoring benefit with one nearby employer."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://schooltutoring.com/corporate/corporate-partners/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Pilot a tutoring benefit with one nearby employer.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-two-family-referrals",
      "kind": "idea",
      "title": "Two-family referrals",
      "categories": [
        "Growth and enrolment"
      ],
      "originating_bots": [
        "Bunny",
        "Steve",
        "Bruno"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Two-family referrals: Consider a modest benefit for both families after a genuine milestone.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Consider a modest benefit for both families after a genuine milestone."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://referral-factory.com/learn/case-study-education",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bunny",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Consider a modest benefit for both families after a genuine milestone.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        },
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Consider a modest benefit for both families after a genuine milestone.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        },
        {
          "originating_bot": "Bruno",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Consider a modest benefit for both families after a genuine milestone.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-review-invitations",
      "kind": "idea",
      "title": "Review invitations",
      "categories": [
        "Growth and enrolment",
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Steve",
        "Benji",
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Review invitations: Invite honest feedback after progress, without incentives or filtering unhappy families.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Invite honest feedback after progress, without incentives or filtering unhappy families."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://doi.org/10.1177/00222429221143329",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Invite honest feedback after progress, without incentives or filtering unhappy families.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        },
        {
          "originating_bot": "Benji",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Invite honest feedback after progress, without incentives or filtering unhappy families.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        },
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Invite honest feedback after progress, without incentives or filtering unhappy families.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings.",
        "No review incentives or review gating; invite honest feedback without filtering unhappy families."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-grade-nine",
      "kind": "idea",
      "title": "Grade 9 readiness checks",
      "categories": [
        "Growth and enrolment"
      ],
      "originating_bots": [
        "Steve"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Grade 9 readiness checks: Help Grade 8 families prepare for the transition.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Help Grade 8 families prepare for the transition."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.tdsb.on.ca/High-School/Going-to-High-School/Beyond-8/Course-Selection",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Help Grade 8 families prepare for the transition.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-university-deadlines",
      "kind": "idea",
      "title": "University-deadline support",
      "categories": [
        "Growth and enrolment"
      ],
      "originating_bots": [
        "Steve"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "University-deadline support: Align senior-school offers with verified admissions dates.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Align senior-school offers with verified admissions dates."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://guidance.ouac.on.ca/resources/schedule-of-dates/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Align senior-school offers with verified admissions dates.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-exam-prep",
      "kind": "idea",
      "title": "January exam preparation",
      "categories": [
        "Growth and enrolment"
      ],
      "originating_bots": [
        "Steve"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "January exam preparation: Offer a short preparation block after checking exam rules and dates.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Offer a short preparation block after checking exam rules and dates."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.ontario.ca/page/student-assessment-evaluations-and-report-cards",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Offer a short preparation block after checking exam rules and dates.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-eqao",
      "kind": "idea",
      "title": "Spring EQAO familiarization",
      "categories": [
        "Growth and enrolment"
      ],
      "originating_bots": [
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Spring EQAO familiarization: Combine online-format familiarity with reading and math practice.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Combine online-format familiarity with reading and math practice."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.eqao.com/the-assessments/junior-division/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Combine online-format familiarity with reading and math practice.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-math-confidence",
      "kind": "idea",
      "title": "Math-confidence assessments",
      "categories": [
        "Growth and enrolment"
      ],
      "originating_bots": [
        "Bunny"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Math-confidence assessments: Offer a supportive diagnostic, not fear-based messaging about provincial results.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Offer a supportive diagnostic, not fear-based messaging about provincial results."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.eqao.com/about-eqao/news-release/assessment-results-2026/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bunny",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Offer a supportive diagnostic, not fear-based messaging about provincial results.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-gauss",
      "kind": "idea",
      "title": "Gauss contest preparation",
      "categories": [
        "Growth and enrolment"
      ],
      "originating_bots": [
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Gauss contest preparation: Explore an enrichment group; check registration eligibility before promising a contest sitting.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Explore an enrichment group; check registration eligibility before promising a contest sitting."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://cemc.uwaterloo.ca/contests/gauss",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Explore an enrichment group; check registration eligibility before promising a contest sitting.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-winter-challenges",
      "kind": "idea",
      "title": "Winter-break challenges",
      "categories": [
        "Growth and enrolment"
      ],
      "originating_bots": [
        "Steve"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Winter-break challenges: Send small optional activities to keep students practising.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Send small optional activities to keep students practising."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://doi.org/10.5296/ijld.v13i2.20819",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Send small optional activities to keep students practising.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-consent-renewal",
      "kind": "idea",
      "title": "Consent renewal",
      "categories": [
        "Growth and enrolment"
      ],
      "originating_bots": [
        "Steve"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Consent renewal: Seek compliant recorded opt-in while an existing consent basis remains valid; consent is revocable, not permanent permission.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Seek compliant recorded opt-in while an existing consent basis remains valid; consent is revocable, not permanent permission."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://crtc.gc.ca/eng/com500/guide.htm",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Seek compliant recorded opt-in while an existing consent basis remains valid; consent is revocable, not permanent permission.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-scan-to-text",
      "kind": "idea",
      "title": "Scan-to-text enquiries",
      "categories": [
        "Growth and enrolment"
      ],
      "originating_bots": [
        "Steve"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Scan-to-text enquiries: Use different enquiry keywords on flyers and signs; an enquiry is not unrestricted marketing consent.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Use different enquiry keywords on flyers and signs; an enquiry is not unrestricted marketing consent."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.txtimpact.com/blog/qr-code-to-text",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Use different enquiry keywords on flyers and signs; an enquiry is not unrestricted marketing consent.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-reserve-slot",
      "kind": "idea",
      "title": "Reserve-your-slot messages",
      "categories": [
        "Growth and enrolment",
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Steve"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Reserve-your-slot messages: Make re-enrolment easy with a reply, without invented scarcity.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Make re-enrolment easy with a reply, without invented scarcity."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.moobicast.com/singapore-tuition-centres-reduce-dropouts-whatsapp-sms.html",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Make re-enrolment easy with a reply, without invented scarcity.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-next-chapter",
      "kind": "idea",
      "title": "Next-chapter conversations",
      "categories": [
        "Growth and enrolment",
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Benji"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Next-chapter conversations: Discuss the next learning goal before the current goal ends.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Discuss the next learning goal before the current goal ends."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.tutorlab.uk/blog/how-to-retain-tutoring-students",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Benji",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Discuss the next learning goal before the current goal ends.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-standby",
      "kind": "idea",
      "title": "Cancellation standby lists",
      "categories": [
        "Growth and enrolment",
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Steve"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Cancellation standby lists: Offer cancelled slots to families who requested alternatives.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Offer cancelled slots to families who requested alternatives."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://elevoi.ca/sms-campaigns-for-tutoring-centers",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Offer cancelled slots to families who requested alternatives.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-badges",
      "kind": "idea",
      "title": "Shareable milestone badges",
      "categories": [
        "Growth and enrolment",
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Steve"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Shareable milestone badges: Celebrate verified competencies while protecting children's privacy.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Celebrate verified competencies while protecting children's privacy."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://blog.issuebadge.com/Use-Cases-By-Industry/11-tutoring-centers-badges-use-case.html",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Growth and enrolment",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Celebrate verified competencies while protecting children's privacy.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-rednote",
      "kind": "idea",
      "title": "RedNote / Xiaohongshu",
      "categories": [
        "New audiences and channels"
      ],
      "originating_bots": [
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "RedNote / Xiaohongshu: Explore reaching Chinese-speaking local parents; the specific supporting article needs checking.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Explore reaching Chinese-speaking local parents; the specific supporting article needs checking."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://connectifylife.com",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / New audiences and channels",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Explore reaching Chinese-speaking local parents; the specific supporting article needs checking.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-library-workshops",
      "kind": "idea",
      "title": "Library workshops",
      "categories": [
        "New audiences and channels"
      ],
      "originating_bots": [
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Library workshops: Investigate a helpful parent workshop through the library proposal process.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Investigate a helpful parent workshop through the library proposal process."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.rhpl.ca",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / New audiences and channels",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Investigate a helpful parent workshop through the library proposal process.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-calendar-posts",
      "kind": "idea",
      "title": "School-calendar business posts",
      "categories": [
        "New audiences and channels"
      ],
      "originating_bots": [
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "School-calendar business posts: Plan useful Google Business Profile posts around local school events.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Plan useful Google Business Profile posts around local school events."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://flento.io",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / New audiences and channels",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Plan useful Google Business Profile posts around local school events.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-whatsapp",
      "kind": "idea",
      "title": "WhatsApp communities",
      "categories": [
        "New audiences and channels"
      ],
      "originating_bots": [
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "WhatsApp communities: Explore optional announcements; check current privacy and account restrictions first.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Explore optional announcements; check current privacy and account restrictions first."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.wavesflo.com/blog/whatsapp-for-coaching-institutes",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / New audiences and channels",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Explore optional announcements; check current privacy and account restrictions first.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-nextdoor",
      "kind": "idea",
      "title": "Nextdoor offers",
      "categories": [
        "New audiences and channels"
      ],
      "originating_bots": [
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Nextdoor offers: Investigate neighbourhood discovery and a free-assessment offer, subject to Canadian availability.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Investigate neighbourhood discovery and a free-assessment offer, subject to Canadian availability."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://business.nextdoor.com/en-us/advertise-with-deals",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / New audiences and channels",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Investigate neighbourhood discovery and a free-assessment offer, subject to Canadian availability.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-search-pages",
      "kind": "idea",
      "title": "Clearer website pages for search",
      "categories": [
        "New audiences and channels"
      ],
      "originating_bots": [
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Clearer website pages for search: Describe actual subjects, grade bands and neighbourhoods clearly; do not promise AI recommendations.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Describe actual subjects, grade bands and neighbourhoods clearly; do not promise AI recommendations."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.aisearchready.ca/resources/industry-ai-visibility/local-ai-search-for-tutoring-centres/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / New audiences and channels",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Describe actual subjects, grade bands and neighbourhoods clearly; do not promise AI recommendations.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-threads",
      "kind": "idea",
      "title": "Threads parent questions",
      "categories": [
        "New audiences and channels"
      ],
      "originating_bots": [
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Threads parent questions: Try short helpful written answers rather than another video-heavy channel.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Try short helpful written answers rather than another video-heavy channel."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://10lab.ai/en/blog/threads-education-marketing-hong-kong/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / New audiences and channels",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Try short helpful written answers rather than another video-heavy channel.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-shorts",
      "kind": "idea",
      "title": "YouTube Shorts",
      "categories": [
        "New audiences and channels"
      ],
      "originating_bots": [
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "YouTube Shorts: Reuse suitable tutor introductions and explanations beyond Instagram.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Reuse suitable tutor introductions and explanations beyond Instagram."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://fracmo.ai/blog/video-for-schools-tutors-guide.html",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / New audiences and channels",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Reuse suitable tutor introductions and explanations beyond Instagram.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-parent-groups",
      "kind": "idea",
      "title": "Parent-group introductions",
      "categories": [
        "New audiences and channels"
      ],
      "originating_bots": [
        "Mark"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Parent-group introductions: Ask for a genuine introduction to an existing school or condo group rather than dropping advertisements; independently review source.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Ask for a genuine introduction to an existing school or condo group rather than dropping advertisements; independently review source."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.gullysales.com/blog/using-parent-groups-and-community-to-bring-in-admissions",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Mark",
          "record": "Leo Nov 7 weekly review / New audiences and channels",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Ask for a genuine introduction to an existing school or condo group rather than dropping advertisements; independently review source.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-weekly-sentence",
      "kind": "idea",
      "title": "One useful weekly sentence",
      "categories": [
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Bruno"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "One useful weekly sentence: Tell each parent one specific thing their child should improve.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Tell each parent one specific thing their child should improve."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.sciencedirect.com/science/article/abs/pii/S0272775715000497",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bruno",
          "record": "Leo Nov 7 weekly review / Parent engagement and retention",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Tell each parent one specific thing their child should improve.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-home-tips",
      "kind": "idea",
      "title": "Tiny home-practice tips",
      "categories": [
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Bruno"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Tiny home-practice tips: Add one manageable activity tied to current learning.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Add one manageable activity tied to current learning."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.nber.org/papers/w20659",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bruno",
          "record": "Leo Nov 7 weekly review / Parent engagement and retention",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Add one manageable activity tied to current learning.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-heads-up",
      "kind": "idea",
      "title": "Targeted heads-up messages",
      "categories": [
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Bruno"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Targeted heads-up messages: Flag a real missed assignment or difficulty when action would help.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Flag a real missed assignment or difficulty when action would help."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://jhr.uwpress.org/content/56/1/125",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bruno",
          "record": "Leo Nov 7 weekly review / Parent engagement and retention",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Flag a real missed assignment or difficulty when action would help.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-monthly-rollups",
      "kind": "idea",
      "title": "Monthly progress rollups",
      "categories": [
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Bruno"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Monthly progress rollups: Summarize attendance, topics and one meaningful progress observation.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Summarize attendance, topics and one meaningful progress observation."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://jhr.uwpress.org/content/60/4/1284",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bruno",
          "record": "Leo Nov 7 weekly review / Parent engagement and retention",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Summarize attendance, topics and one meaningful progress observation.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-joint-prompts",
      "kind": "idea",
      "title": "Parent-and-student practice prompts",
      "categories": [
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Bruno",
        "Bunny"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Parent-and-student practice prompts: Include the student in appropriate home-practice communication with permission.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Include the student in appropriate home-practice communication with permission."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://doi.org/10.3102/0013189X251331518",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bruno",
          "record": "Leo Nov 7 weekly review / Parent engagement and retention",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Include the student in appropriate home-practice communication with permission.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        },
        {
          "originating_bot": "Bunny",
          "record": "Leo Nov 7 weekly review / Parent engagement and retention",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Include the student in appropriate home-practice communication with permission.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-showcases",
      "kind": "idea",
      "title": "Student-led showcases",
      "categories": [
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Benji"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Student-led showcases: Let children explain selected work and their next goal to parents.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Let children explain selected work and their next goal to parents."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://pbsapril.edublogs.org/2026/05/26/student-led-conference-success/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Benji",
          "record": "Leo Nov 7 weekly review / Parent engagement and retention",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Let children explain selected work and their next goal to parents.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-independence",
      "kind": "idea",
      "title": "Independence tracking",
      "categories": [
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Bunny"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Independence tracking: Record whether work was completed alone, with a hint or after a model.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Record whether work was completed alone, with a hint or after a model."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://nssa.stanford.edu/tutoring/learning-integration/stakeholder-engagement/tutor-student-goal-setting-conferences",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bunny",
          "record": "Leo Nov 7 weekly review / Parent engagement and retention",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Record whether work was completed alone, with a hint or after a model.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-parent-practice",
      "kind": "idea",
      "title": "Parent-supported practice",
      "categories": [
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Bunny"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Parent-supported practice: Explore a brief guided parent handoff; do not assume parents can replace tutoring time.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Explore a brief guided parent handoff; do not assume parents can replace tutoring time."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.wwhge.org/wp-content/uploads/2025/10/Cheaper-by-the-dozen-tutoring-AB-testing_WP_2025001_updated.pdf",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bunny",
          "record": "Leo Nov 7 weekly review / Parent engagement and retention",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Explore a brief guided parent handoff; do not assume parents can replace tutoring time.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-drifting-students",
      "kind": "idea",
      "title": "Early check-ins for drifting students",
      "categories": [
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Steve"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Early check-ins for drifting students: Identify disengagement before a family leaves; specific evidence behind the Pillar OS submission remains unchecked.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Identify disengagement before a family leaves; specific evidence behind the Pillar OS submission remains unchecked."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": "Exact URL unavailable in weekly review; recover original record rather than invent citation."
      },
      "sources": [],
      "source_records": [
        {
          "originating_bot": "Steve",
          "record": "Leo Nov 7 weekly review / Parent engagement and retention",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Identify disengagement before a family leaves; specific evidence behind the Pillar OS submission remains unchecked.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-attendance-counts",
      "kind": "idea",
      "title": "Exact attendance-count messages",
      "categories": [
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Bruno"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Exact attendance-count messages: Make attendance concrete; Rogers–Feller research citation still needs recovering.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Make attendance concrete; Rogers–Feller research citation still needs recovering."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": "Exact URL unavailable in weekly review; recover original record rather than invent citation."
      },
      "sources": [],
      "source_records": [
        {
          "originating_bot": "Bruno",
          "record": "Leo Nov 7 weekly review / Parent engagement and retention",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Make attendance concrete; Rogers–Feller research citation still needs recovering.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-parent-clips",
      "kind": "idea",
      "title": "Short parent progress clips",
      "categories": [
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Bunny"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Short parent progress clips: Show learning with short parent-facing clips; original ClassDojo/Edutopia source links need recovering.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Show learning with short parent-facing clips; original ClassDojo/Edutopia source links need recovering."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": "Exact URL unavailable in weekly review; recover original record rather than invent citation."
      },
      "sources": [],
      "source_records": [
        {
          "originating_bot": "Bunny",
          "record": "Leo Nov 7 weekly review / Parent engagement and retention",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Show learning with short parent-facing clips; original ClassDojo/Edutopia source links need recovering.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-reflection-videos",
      "kind": "idea",
      "title": "Student reflection videos",
      "categories": [
        "Parent engagement and retention"
      ],
      "originating_bots": [
        "Bunny"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Student reflection videos: Let students reflect on learning in videos; related to parent clips but a distinct activity. Original ClassDojo/Edutopia source links need recovering.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Let students reflect on learning in videos; related to parent clips but a distinct activity. Original ClassDojo/Edutopia source links need recovering."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": "Exact URL unavailable in weekly review; recover original record rather than invent citation."
      },
      "sources": [],
      "source_records": [
        {
          "originating_bot": "Bunny",
          "record": "Leo Nov 7 weekly review / Parent engagement and retention",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Let students reflect on learning in videos; related to parent clips but a distinct activity. Original ClassDojo/Edutopia source links need recovering.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-faded-examples",
      "kind": "idea",
      "title": "Faded worked examples",
      "categories": [
        "Teaching–Professor ideas",
        "Learning Dragon ideas"
      ],
      "originating_bots": [
        "Bunny",
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Faded worked examples: Gradually remove solution steps before independent practice.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Gradually remove solution steps before independent practice."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12879535/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bunny",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Gradually remove solution steps before independent practice.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        },
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Gradually remove solution steps before independent practice.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-spaced-review",
      "kind": "idea",
      "title": "Spaced review strips",
      "categories": [
        "Teaching–Professor ideas"
      ],
      "originating_bots": [
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Spaced review strips: Revisit earlier skills briefly in later packages.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Revisit earlier skills briefly in later packages."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://doi.org/10.1007/s10648-025-10035-1",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Revisit earlier skills briefly in later packages.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-interleaving",
      "kind": "idea",
      "title": "Interleaved practice",
      "categories": [
        "Teaching–Professor ideas",
        "Learning Dragon ideas"
      ],
      "originating_bots": [
        "Bunny"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Interleaved practice: Mix suitable problem types so students must choose a method.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Mix suitable problem types so students must choose a method."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://doi.org/10.1007/s10648-026-10225-5",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bunny",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Mix suitable problem types so students must choose a method.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-confidence",
      "kind": "idea",
      "title": "Confidence ratings",
      "categories": [
        "Teaching–Professor ideas"
      ],
      "originating_bots": [
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Confidence ratings: Compare confidence with correctness to guide feedback.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Compare confidence with correctness to guide feedback."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://doi.org/10.1007/s10649-021-10084-7",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Compare confidence with correctness to guide feedback.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-wodb",
      "kind": "idea",
      "title": "Which One Doesn’t Belong?",
      "categories": [
        "Teaching–Professor ideas"
      ],
      "originating_bots": [
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Which One Doesn’t Belong?: Use a short reasoning warm-up with defensible explanations.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Use a short reasoning warm-up with defensible explanations."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://wodb.ca",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Use a short reasoning warm-up with defensible explanations.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-open-middle",
      "kind": "idea",
      "title": "Open Middle challenges",
      "categories": [
        "Teaching–Professor ideas"
      ],
      "originating_bots": [
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Open Middle challenges: Add a small original stretch section without replacing regular practice.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Add a small original stretch section without replacing regular practice."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.openmiddle.com/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Add a small original stretch section without replacing regular practice.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-repeated-reading",
      "kind": "idea",
      "title": "Repeated reading",
      "categories": [
        "Teaching–Professor ideas"
      ],
      "originating_bots": [
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Repeated reading: Reread a passage toward an appropriate goal, with optional self-graphing.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Reread a passage toward an appropriate goal, with optional self-graphing."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://journals.sagepub.com/doi/10.1177/07419325040250040801",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Reread a passage toward an appropriate goal, with optional self-graphing.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-find-fix",
      "kind": "idea",
      "title": "Find-and-fix mistakes",
      "categories": [
        "Teaching–Professor ideas"
      ],
      "originating_bots": [
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Find-and-fix mistakes: Explain and correct a realistic misconception.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Explain and correct a realistic misconception."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://doi.org/10.1007/s40593-015-0064-x",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Explain and correct a realistic misconception.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-estimation",
      "kind": "idea",
      "title": "Estimation warm-ups",
      "categories": [
        "Teaching–Professor ideas"
      ],
      "originating_bots": [
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Estimation warm-ups: Give a low, high and best estimate before a reveal.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Give a low, high and best estimate before a reveal."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://estimation180.com/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Give a low, high and best estimate before a reveal.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-bar-models",
      "kind": "idea",
      "title": "Bar-model word problems",
      "categories": [
        "Teaching–Professor ideas"
      ],
      "originating_bots": [
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Bar-model word problems: Gradually fade diagram support as students learn to represent the problem.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Gradually fade diagram support as students learn to represent the problem."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://link.springer.com/article/10.1007/s10649-022-10150-8",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Gradually fade diagram support as students learn to represent the problem.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-fraction-talks",
      "kind": "idea",
      "title": "Fraction Talks",
      "categories": [
        "Teaching–Professor ideas"
      ],
      "originating_bots": [
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Fraction Talks: Reason about shaded areas and the relationship between a part and its whole.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Reason about shaded areas and the relationship between a part and its whole."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://fractiontalks.com/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Reason about shaded areas and the relationship between a part and its whole.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-visual-patterns",
      "kind": "idea",
      "title": "Growing visual patterns",
      "categories": [
        "Teaching–Professor ideas"
      ],
      "originating_bots": [
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Growing visual patterns: Predict figures and explain a general rule.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Predict figures and explain a general rule."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.visualpatterns.org/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Predict figures and explain a general rule.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-would-you-rather",
      "kind": "idea",
      "title": "Would You Rather Math",
      "categories": [
        "Teaching–Professor ideas"
      ],
      "originating_bots": [
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Would You Rather Math: Calculate two options and justify a choice.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Calculate two options and justify a choice."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://www.wouldyourathermath.com/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Calculate two options and justify a choice.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-same-surface",
      "kind": "idea",
      "title": "Same-looking, different-method problems",
      "categories": [
        "Teaching–Professor ideas"
      ],
      "originating_bots": [
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Same-looking, different-method problems: Use one shared picture with questions requiring different mathematical methods.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Use one shared picture with questions requiring different mathematical methods."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://ssddproblems.com/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Use one shared picture with questions requiring different mathematical methods.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-sentence-combining",
      "kind": "idea",
      "title": "Sentence combining",
      "categories": [
        "Teaching–Professor ideas"
      ],
      "originating_bots": [
        "Professor"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Sentence combining: Combine short sentences, then gradually remove cue words.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Combine short sentences, then gradually remove cue words."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://doi.org/10.1037/0022-0663.97.1.43",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Professor",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Combine short sentences, then gradually remove cue words.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-vocabulary",
      "kind": "idea",
      "title": "Spaced vocabulary recall",
      "categories": [
        "Teaching–Professor ideas",
        "Learning Dragon ideas"
      ],
      "originating_bots": [
        "Bunny"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Spaced vocabulary recall: Bring back a newly learned word after intervening story material.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Bring back a newly learned word after intervening story material."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12263187/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bunny",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Bring back a newly learned word after intervening story material.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-french-decoding",
      "kind": "idea",
      "title": "French-specific decoding",
      "categories": [
        "Teaching–Professor ideas",
        "Learning Dragon ideas"
      ],
      "originating_bots": [
        "Bunny"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "French-specific decoding: Build French sequences around French sound–letter relationships, not translated English lessons.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Build French sequences around French sound–letter relationships, not translated English lessons."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://link.springer.com/article/10.1007/s40692-019-00152-6",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bunny",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Build French sequences around French sound–letter relationships, not translated English lessons.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-interest-contexts",
      "kind": "idea",
      "title": "Interest-based problem contexts",
      "categories": [
        "Teaching–Professor ideas",
        "Learning Dragon ideas"
      ],
      "originating_bots": [
        "Bunny"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Interest-based problem contexts: Personalize the problem setting while preserving mathematical demand.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Personalize the problem setting while preserving mathematical demand."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://link.springer.com/article/10.1007/s40593-025-00491-9",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bunny",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Personalize the problem setting while preserving mathematical demand.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-split-facts",
      "kind": "idea",
      "title": "Split fact practice",
      "categories": [
        "Teaching–Professor ideas",
        "Learning Dragon ideas"
      ],
      "originating_bots": [
        "Bunny"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Split fact practice: Investigate short separated fluency drills while keeping multi-step work together.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Investigate short separated fluency drills while keeping multi-step work together."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": null
      },
      "sources": [
        {
          "url": "https://pubmed.ncbi.nlm.nih.gov/41478700/",
          "verification_status": "unchecked",
          "verified_at": null,
          "provenance": "URL exactly as supplied in Leo Nov 7 weekly review"
        }
      ],
      "source_records": [
        {
          "originating_bot": "Bunny",
          "record": "Leo Nov 7 weekly review / Teaching–Professor ideas",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Investigate short separated fluency drills while keeping multi-step work together.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Create original content, not copied worksheets. Preserve required core practice; no expansion of current development scope without user choice."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-idea-family-name-preflight",
      "kind": "idea",
      "title": "Validated family-name correction list",
      "categories": [
        "Miscellaneous"
      ],
      "originating_bots": [
        "Leo"
      ],
      "received_date": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Validated family-name correction list: Check confirmed corrections before nightly emails so the same confirmed corrections do not repeatedly become holds.",
      "implementation_advice": {
        "kind": "bot_suggested_not_original_source_evidence",
        "text": "Check confirmed corrections before nightly emails so the same confirmed corrections do not repeatedly become holds."
      },
      "evidence": {
        "verification_status": "unchecked",
        "claim": "Relayed weekly proposal only; citation content not opened or verified here.",
        "missing_source_note": "Exact URL unavailable in weekly review; recover original record rather than invent citation."
      },
      "sources": [],
      "source_records": [
        {
          "originating_bot": "Leo",
          "record": "Leo Nov 7 weekly review / Miscellaneous",
          "received_period": "2026-10-31/2026-11-07",
          "review_proposal_text": "Check confirmed corrections before nightly emails so the same confirmed corrections do not repeatedly become holds.",
          "original_submission_available": false,
          "note": "Merged attribution from review; independent per-bot wording unavailable."
        }
      ],
      "cautions": [
        "Proposal only; not approved or implemented.",
        "Efficacy, statistical claims, dates and local applicability remain unchecked; no quantitative outcome claim is warranted.",
        "Before outreach check applicable CASL consent, identification and unsubscribe requirements; an enquiry is not blanket marketing permission.",
        "Protect child/family privacy; obtain appropriate permission before sharing identifying work, images or recordings."
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    }
  ]
}
```

## C. weekly-performance.json

```json
{
  "metadata": {
    "schema_version": 1,
    "prepared_on": "2026-11-07",
    "timezone": "America/Toronto",
    "provenance": "Supplied parent conversation; no web research",
    "chronology_note": "Period-only received dates: display Oct 31–Nov 7, 2026; original discovery dates unknown. Title/ID tie-break is not discovery order.",
    "privacy_note": "No private child/parent contacts, credentials, invented notes or approvals."
  },
  "records": [
    {
      "id": "sparky-performance-2026-11-07-johnny",
      "kind": "weekly_performance",
      "bot": "Johnny",
      "title": "Johnny — weekly review",
      "categories": [
        "Weekly bots performance"
      ],
      "period": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Monday through Saturday Scheduler and progress-file watchdog checks all passed.",
      "caveats": [
        "Relayed review only; underlying records not independently audited here.",
        "Partial recovered review; not a complete audit."
      ],
      "verification_status": "relayed_unverified",
      "sources": [
        {
          "record": "Leo Nov 7 weekly review in supplied parent context"
        }
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-performance-2026-11-07-professor",
      "kind": "weekly_performance",
      "bot": "Professor",
      "title": "Professor — weekly review",
      "categories": [
        "Weekly bots performance"
      ],
      "period": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "v61 published Friday with matching hashes. Later geometry work remains unpublished and not release-ready; visual/coverage concerns remain.",
      "caveats": [
        "Local docs checked: Nov 6 publication at 2:59:25 PM EST. Combined geometry full suite 77/78 groups passed and nightly 319/322; one focused v53 assertion remained, and nightly failures were not cleared. Targeted passes do not supersede failed combined tests.",
        "Partial recovered review; not a complete audit."
      ],
      "verification_status": "documented_partial",
      "sources": [
        {
          "path": "/workspace/professor/dev/dist/release_v61/PUBLICATION_STATUS.md",
          "lines": "3–18"
        },
        {
          "path": "/workspace/professor/dev/dist/v62_geometry_review/STATUS.md",
          "lines": "67–80"
        }
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-performance-2026-11-07-bunny",
      "kind": "weekly_performance",
      "bot": "Bunny",
      "title": "Bunny — weekly review",
      "categories": [
        "Weekly bots performance"
      ],
      "period": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Record reports 412 reading-book photos copied and a 36-screen Lesson 1 walkthrough, with two screen gaps disclosed.",
      "caveats": [
        "Useful research, not proof the whole library is fully analysed; relayed report not independently audited.",
        "Partial recovered review; not a complete audit."
      ],
      "verification_status": "relayed_unverified",
      "sources": [
        {
          "record": "Leo Nov 7 weekly review in supplied parent context"
        }
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-performance-2026-11-07-benji",
      "kind": "weekly_performance",
      "bot": "Benji",
      "title": "Benji — weekly review",
      "categories": [
        "Weekly bots performance"
      ],
      "period": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "User reported first customer-engagement task went well; workflow now uses SMS rather than check-in emails.",
      "caveats": [
        "Unresolved student-record conflicts need care; no independent outcome audit.",
        "Partial recovered review; not a complete audit."
      ],
      "verification_status": "relayed_unverified",
      "sources": [
        {
          "record": "Leo Nov 7 weekly review in supplied parent context"
        }
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-performance-2026-11-07-steve",
      "kind": "weekly_performance",
      "bot": "Steve",
      "title": "Steve — weekly review",
      "categories": [
        "Weekly bots performance"
      ],
      "period": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Log records five approved catch-up SMS sends and an approved parent reply.",
      "caveats": [
        "Send activity is not proof recipients read them. Personal contacts excluded.",
        "Partial recovered review; not a complete audit."
      ],
      "verification_status": "relayed_unverified",
      "sources": [
        {
          "record": "Leo Nov 7 weekly review in supplied parent context"
        }
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-performance-2026-11-07-bruno",
      "kind": "weekly_performance",
      "bot": "Bruno",
      "title": "Bruno — weekly review",
      "categories": [
        "Weekly bots performance"
      ],
      "period": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Personalized family reports underway; missing parent names and student aliases caused holds.",
      "caveats": [
        "Finding a correction does not confirm a previously missed report was subsequently sent.",
        "Partial recovered review; not a complete audit."
      ],
      "verification_status": "relayed_unverified",
      "sources": [
        {
          "record": "Leo Nov 7 weekly review in supplied parent context"
        }
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-performance-2026-11-07-mark",
      "kind": "weekly_performance",
      "bot": "Mark",
      "title": "Mark — weekly review",
      "categories": [
        "Weekly bots performance"
      ],
      "period": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Supplied growth ideas and engagement proposals.",
      "caveats": [
        "Actual posting outcomes not fully verified.",
        "Partial recovered review; not a complete audit."
      ],
      "verification_status": "relayed_unverified",
      "sources": [
        {
          "record": "Leo Nov 7 weekly review in supplied parent context"
        }
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-performance-2026-11-07-wilma",
      "kind": "weekly_performance",
      "bot": "Wilma",
      "title": "Wilma — weekly review",
      "categories": [
        "Weekly bots performance"
      ],
      "period": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Insufficient checked evidence to grade the week fairly.",
      "caveats": [
        "No full audit; unknown is not failure.",
        "Partial recovered review; not a complete audit."
      ],
      "verification_status": "relayed_unverified",
      "sources": [
        {
          "record": "Leo Nov 7 weekly review in supplied parent context"
        }
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-performance-2026-11-07-cricket",
      "kind": "weekly_performance",
      "bot": "Cricket",
      "title": "Cricket — weekly review",
      "categories": [
        "Weekly bots performance"
      ],
      "period": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Insufficient checked evidence to grade the week fairly.",
      "caveats": [
        "No full audit; unknown is not failure.",
        "Partial recovered review; not a complete audit."
      ],
      "verification_status": "relayed_unverified",
      "sources": [
        {
          "record": "Leo Nov 7 weekly review in supplied parent context"
        }
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    },
    {
      "id": "sparky-performance-2026-11-07-leo",
      "kind": "weekly_performance",
      "bot": "Leo",
      "title": "Leo — weekly review",
      "categories": [
        "Weekly bots performance"
      ],
      "period": {
        "start": "2026-10-31",
        "end": "2026-11-07",
        "granularity": "period",
        "timezone": "America/Toronto",
        "original_discovery_at": null
      },
      "summary": "Meeting review was late; scheduled run failed for unavailable usage and separate review ended in error. Recovered review was incomplete.",
      "caveats": [
        "Why purchased credits did not cover the failure remains unverified; do not infer monthly cap or credit balance cause.",
        "Partial recovered review; not a complete audit."
      ],
      "verification_status": "relayed_unverified",
      "sources": [
        {
          "record": "Leo Nov 7 weekly review in supplied parent context"
        }
      ],
      "user_state": {
        "status": "unreviewed",
        "notes": "",
        "approval": null
      }
    }
  ]
}
```
