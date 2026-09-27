# 🐾 PetOlife Family Care

## One Pet. One Family. One Care Score.

PetOlife Family Care is a shared family pet-care system designed to help multiple family members coordinate the daily care of one pet.

The system keeps everyone informed about what needs to be done, what has already been completed, who completed it, and when it was completed.

---

## 🎯 Problem

Pet care is often shared between family members.

One person may take the pet for a walk, another may provide food, while someone else may handle medication.

Without a shared system, family members may not know:

- What is pending?
- Who completed the task?
- When was it completed?
- Was an important care activity missed?

---

## 💡 Solution

PetOlife Family Care provides a shared dashboard where family members can manage daily pet-care activities.

The system provides:

- Shared daily checklist
- Family member selection
- Task completion tracking
- Completion time
- Real-time shared task status
- Smart reminders
- Weighted Care Score
- Pet Health ID
- Recent activity history

---

## 🐶 Pet Profile

Demo Pet:

- Name: Jessie
- Breed: Golden Retriever
- Age: 3 Years
- Gender: Female

---

## 👨‍👩‍👦 Family Members

The prototype supports multiple family members:

- Dad
- Mom
- Son

When one member completes a task, the shared state is updated for the family.

---

## 📋 Daily Care Activities

The prototype includes:

- Morning Walk
- Morning Food
- Water Bowl Change
- Medicine
- Evening Walk
- Grooming

Each activity has a different weight depending on its importance.

---

## ❤️ Care Score

The Care Score is calculated out of 100.

Different activities contribute different weights.

### Example weighting

- Medical Care: 25 points
- Nutrition: 20 points
- Hydration: 10 points
- Exercise: 35 points
- Hygiene: 10 points

Important medical activities therefore have greater influence on the overall score.

---

## 🔔 Smart Reminders

Pending activities are displayed as reminders.

For example:

"Jessie's Medicine is pending"

Medical tasks receive additional visual priority because missing medication can be more important than missing a routine activity.

---

## 🩺 Pet Health ID

Each pet has a Health ID section containing:

- Pet identity
- Breed
- Age
- Gender
- Vaccination status
- Medication tracking status
- Family access status
- Pet Health ID

Demo ID:

PET-JES-2026-001

---

## 📊 Recent Activity

The system records completed activities with:

- Family member name
- Activity name
- Completion time

Example:

Dad completed Morning Walk at 7:24 AM.

---

## ⚡ Shared Family Experience

The prototype maintains shared task state so that family members can see task updates from the same application.

This allows the family to coordinate care without duplicating tasks.

---

## 🛠️ Technology

- Python
- Flask
- HTML
- CSS
- JavaScript

---

## ▶️ Running the Project

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
