/**
 * UNYQ Finance 2.0 — Deterministic Financial Planning & Simulation Engine
 * Pure functions, timezone-safe (UTC calendar arithmetic), zero external dependencies.
 */

export function toNum(val, fallback = 0) {
  if (val === null || val === undefined || val === "") return fallback;
  if (typeof val === "number") return Number.isFinite(val) ? val : fallback;
  const cleaned = String(val).trim().replace(",", ".");
  const parsed = Number.parseFloat(cleaned);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export function round2(val) {
  return Math.round((toNum(val) + Number.EPSILON) * 100) / 100;
}

export function todayIso() {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function currentMonthIso() {
  return todayIso().slice(0, 7);
}

export function daysInMonth(year, month1Based) {
  return new Date(Date.UTC(year, month1Based, 0)).getUTCDate();
}

export function parseIsoParts(isoStr) {
  if (!isoStr || typeof isoStr !== "string") return null;
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(isoStr.trim());
  if (!m) return null;
  const year = Number.parseInt(m[1], 10);
  const month = Number.parseInt(m[2], 10);
  const day = Number.parseInt(m[3], 10);
  if (!year || month < 1 || month > 12 || day < 1 || day > 31) return null;
  return { year, month, day };
}

export function safeIsoDate(year, month1Based, day) {
  const maxDay = daysInMonth(year, month1Based);
  const clampedDay = Math.min(Math.max(1, Number.parseInt(day, 10) || 1), maxDay);
  return `${String(year).padStart(4, "0")}-${String(month1Based).padStart(2, "0")}-${String(clampedDay).padStart(2, "0")}`;
}

export function addDaysIso(isoStr, offsetDays) {
  const p = parseIsoParts(isoStr);
  if (!p) return todayIso();
  const dt = new Date(Date.UTC(p.year, p.month - 1, p.day + Number(offsetDays || 0)));
  return `${dt.getUTCFullYear()}-${String(dt.getUTCMonth() + 1).padStart(2, "0")}-${String(dt.getUTCDate()).padStart(2, "0")}`;
}

export function addMonthsIso(isoStr, monthsToAdd, preferredDay = null) {
  const p = parseIsoParts(isoStr);
  if (!p) return todayIso();
  const totalMonths = p.year * 12 + (p.month - 1) + Number(monthsToAdd || 0);
  const targetYear = Math.floor(totalMonths / 12);
  const targetMonth = (totalMonths % 12) + 1;
  const targetDay = preferredDay !== null && preferredDay !== undefined ? preferredDay : p.day;
  return safeIsoDate(targetYear, targetMonth, targetDay);
}

export function addMonthsYm(ymStr, monthsToAdd) {
  if (!ymStr || !/^\d{4}-\d{2}/.test(ymStr)) return currentMonthIso();
  const year = Number.parseInt(ymStr.slice(0, 4), 10);
  const month = Number.parseInt(ymStr.slice(5, 7), 10);
  const total = year * 12 + (month - 1) + Number(monthsToAdd || 0);
  const ny = Math.floor(total / 12);
  const nm = (total % 12) + 1;
  return `${String(ny).padStart(4, "0")}-${String(nm).padStart(2, "0")}`;
}

export function diffDaysInclusive(startIso, endIso) {
  const a = parseIsoParts(startIso);
  const b = parseIsoParts(endIso);
  if (!a || !b) return 1;
  const tA = Date.UTC(a.year, a.month - 1, a.day);
  const tB = Date.UTC(b.year, b.month - 1, b.day);
  const diff = Math.round((tB - tA) / 86400000) + 1;
  return Math.max(1, diff);
}

export function getWeekdayIndexMondayFirst(isoStr) {
  const p = parseIsoParts(isoStr);
  if (!p) return 0;
  const jsDay = new Date(Date.UTC(p.year, p.month - 1, p.day)).getUTCDay(); // 0=Sun..6=Sat
  return (jsDay + 6) % 7; // 0=Mon..6=Sun
}

const WEEKDAY_SHORT_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];
const MONTH_NAMES_DE = [
  "Januar", "Februar", "März", "April", "Mai", "Juni",
  "Juli", "August", "September", "Oktober", "November", "Dezember",
];
const MONTH_SHORT_DE = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"];

export function formatWeekdayShort(isoStr) {
  return WEEKDAY_SHORT_DE[getWeekdayIndexMondayFirst(isoStr)] || "";
}

export function formatDateDe(isoStr) {
  const p = parseIsoParts(isoStr);
  if (!p) return "–";
  return `${String(p.day).padStart(2, "0")}.${String(p.month).padStart(2, "0")}.${p.year}`;
}

export function formatDateShortDe(isoStr) {
  const p = parseIsoParts(isoStr);
  if (!p) return "–";
  return `${String(p.day).padStart(2, "0")}.${String(p.month).padStart(2, "0")}.`;
}

export function formatMonthYearDe(ymStr, short = false) {
  if (!ymStr || !/^\d{4}-\d{2}/.test(ymStr)) return "–";
  const y = Number.parseInt(ymStr.slice(0, 4), 10);
  const m = Number.parseInt(ymStr.slice(5, 7), 10);
  const names = short ? MONTH_SHORT_DE : MONTH_NAMES_DE;
  return `${names[m - 1] || m} ${y}`;
}

export function formatMoney(value, currency = "EUR") {
  const num = toNum(value, 0);
  try {
    return new Intl.NumberFormat("de-DE", {
      style: "currency",
      currency: currency || "EUR",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(num);
  } catch {
    return `${num.toFixed(2)} €`;
  }
}

export function formatCompactMoney(value, currency = "EUR") {
  const num = toNum(value, 0);
  const sym = currency === "USD" ? "$" : currency === "CHF" ? "CHF " : "€";
  const abs = Math.abs(num);
  const sign = num < 0 ? "−" : "";
  if (abs >= 10000) {
    return `${sign}${(abs / 1000).toFixed(1).replace(".", ",")}k ${sym}`.trim();
  }
  if (abs >= 1000) {
    return `${sign}${Math.round(abs).toLocaleString("de-DE")} ${sym}`.trim();
  }
  return `${sign}${abs.toFixed(0)} ${sym}`.trim();
}

export function entryUsesDefaultDay(entry) {
  if (!entry || entry.frequency !== "MONTHLY") return false;
  return !entry.due_day && !entry.due_date;
}

export function getEntryEffectiveDay(entry) {
  if (!entry) return 1;
  if (entry.due_day) return Math.min(31, Math.max(1, Number(entry.due_day)));
  if (entry.due_date) {
    const p = parseIsoParts(entry.due_date);
    if (p) return p.day;
  }
  return 1;
}

/**
 * Checks whether a FinanceEntry triggers on a specific ISO calendar date.
 */
export function doesEntryHitDay(entry, dayIso) {
  if (!entry || entry.is_active === false) return false;
  const p = parseIsoParts(dayIso);
  if (!p) return false;

  const freq = entry.frequency || "MONTHLY";
  const dueDate = entry.due_date || null;

  if (freq === "ONCE") {
    return Boolean(dueDate && dueDate === dayIso);
  }

  // Respect future start date if set
  if (dueDate && dayIso < dueDate) {
    return false;
  }

  if (freq === "MONTHLY") {
    const rawDay = getEntryEffectiveDay(entry);
    const maxDay = daysInMonth(p.year, p.month);
    return p.day === Math.min(rawDay, maxDay);
  }

  if (freq === "WEEKLY") {
    const targetWeekday = dueDate ? getWeekdayIndexMondayFirst(dueDate) : 0;
    return getWeekdayIndexMondayFirst(dayIso) === targetWeekday;
  }

  if (freq === "YEARLY") {
    if (!dueDate) {
      return p.month === 1 && p.day === 1;
    }
    const dp = parseIsoParts(dueDate);
    if (!dp) return false;
    const maxDay = daysInMonth(p.year, dp.month);
    return p.month === dp.month && p.day === Math.min(dp.day, maxDay);
  }

  return false;
}

/**
 * Resolves the next upcoming due date of an active Debt relative to referenceIso.
 */
export function resolveDebtNextDueDate(debt, referenceIso) {
  if (!debt || debt.status !== "ACTIVE") return null;
  const remaining = Math.max(0, toNum(debt.total_amount) - toNum(debt.amount_paid));
  if (remaining <= 0.004 || debt.is_fully_paid) return null;

  if (debt.next_due_date) {
    return debt.next_due_date;
  }
  if (debt.payment_type === "FIXED_AMOUNT") {
    return debt.start_date || referenceIso;
  }
  const dueDay = Number(debt.due_day) || (debt.start_date ? parseIsoParts(debt.start_date)?.day : 1) || 1;
  const ref = debt.start_date && debt.start_date > referenceIso ? debt.start_date : referenceIso;
  const rp = parseIsoParts(ref);
  if (!rp) return null;
  let candidate = safeIsoDate(rp.year, rp.month, dueDay);
  if (candidate < ref) {
    candidate = addMonthsIso(candidate, 1, dueDay);
  }
  return candidate;
}

/**
 * Finds the next income date (e.g. next salary) strictly after startIso within 45 days.
 */
export function findNextPaydayIso(entries, startIso = todayIso()) {
  const incomes = (entries || []).filter((e) => e.is_active !== false && e.entry_type === "INCOME" && toNum(e.amount) > 0);
  if (!incomes.length) return addDaysIso(startIso, 30);
  for (let offset = 1; offset <= 45; offset++) {
    const d = addDaysIso(startIso, offset);
    if (incomes.some((inc) => doesEntryHitDay(inc, d))) {
      return d;
    }
  }
  return addDaysIso(startIso, 30);
}

/**
 * Day-by-Day Balance ("Soll-Besitz") & Debt Amortization Timeline Simulator
 */
export function simulateDailyTimeline({
  startDateIso = todayIso(),
  days = 90,
  startingBalance = 0,
  dispoLimit = 0,
  dispoUsed = 0,
  emergencyBuffer = 0,
  entries = [],
  debts = [],
  includeDailyBudget = false,
  dailyLivingBudget = 0,
  extraEvents = [],
  disabledEntryIds = new Set(),
  disabledDebtIds = new Set(),
} = {}) {
  const horizon = Math.max(1, Math.min(731, Number.parseInt(days, 10) || 90));
  const today = todayIso();
  const dailyBudget = includeDailyBudget ? Math.max(0, toNum(dailyLivingBudget)) : 0;
  const dispoAvailable = Math.max(0, toNum(dispoLimit) - toNum(dispoUsed));
  const bufferTarget = Math.max(0, toNum(emergencyBuffer));

  const activeEntries = (entries || []).filter(
    (e) => e && e.is_active !== false && !disabledEntryIds.has(e.id)
  );

  const overdueDebts = [];
  const debtStates = [];

  for (const debt of debts || []) {
    if (!debt || debt.status !== "ACTIVE" || disabledDebtIds.has(debt.id)) continue;
    const rem = round2(Math.max(0, toNum(debt.total_amount) - toNum(debt.amount_paid)));
    if (rem <= 0) continue;

    const pType = debt.payment_type || "INSTALLMENT";
    const rate = pType === "FIXED_AMOUNT" ? rem : Math.max(0, toNum(debt.monthly_payment));
    const dueDay =
      Number(debt.due_day) ||
      (debt.next_due_date ? parseIsoParts(debt.next_due_date)?.day : null) ||
      (debt.start_date ? parseIsoParts(debt.start_date)?.day : null) ||
      1;

    let nextDue = resolveDebtNextDueDate(debt, startDateIso);
    if (nextDue && nextDue < startDateIso) {
      const overdueAmt = pType === "FIXED_AMOUNT" ? rem : Math.min(rem, rate || rem);
      overdueDebts.push({
        id: debt.id,
        name: debt.name,
        dueDate: nextDue,
        amount: round2(overdueAmt),
      });
      if (pType === "INSTALLMENT" && rate > 0) {
        const sp = parseIsoParts(startDateIso);
        let cand = safeIsoDate(sp.year, sp.month, dueDay);
        if (cand < startDateIso) {
          cand = addMonthsIso(cand, 1, dueDay);
        }
        nextDue = cand;
      } else {
        // Keep fixed overdue visible on day 0 only as overdue alert unless rescheduled
        nextDue = null;
      }
    }

    debtStates.push({
      id: debt.id,
      name: debt.name,
      debtKind: debt.debt_kind || "DEBT",
      paymentType: pType,
      dueDay,
      remaining: rem,
      rate,
      nextDue,
    });
  }

  const extraByDate = new Map();
  for (const ev of extraEvents || []) {
    if (!ev || !ev.date) continue;
    if (!extraByDate.has(ev.date)) extraByDate.set(ev.date, []);
    extraByDate.get(ev.date).push(ev);
  }

  const initialDebtTotal = round2(debtStates.reduce((s, d) => s + d.remaining, 0));
  let runningBalance = round2(toNum(startingBalance));
  let minBalance = runningBalance;
  let minBalanceDate = startDateIso;
  let maxBalance = runningBalance;
  let maxBalanceDate = startDateIso;
  let firstNegativeDate = runningBalance < 0 ? startDateIso : null;
  let firstDispoBreachDate = runningBalance < -dispoAvailable ? startDateIso : null;
  let daysInNegative = 0;

  let totalIncome = 0;
  let totalFixedOutflow = 0;
  let totalDebtPaid = 0;
  let totalLivingOutflow = 0;
  const debtsPaidOff = [];
  const timeline = [];

  for (let i = 0; i < horizon; i++) {
    const date = addDaysIso(startDateIso, i);
    const parts = parseIsoParts(date);
    const weekdayIdx = getWeekdayIndexMondayFirst(date);
    const startBal = runningBalance;
    const events = [];
    let incomeDay = 0;
    let outflowDay = 0;

    for (const entry of activeEntries) {
      if (doesEntryHitDay(entry, date)) {
        const amt = round2(Math.abs(toNum(entry.amount)));
        if (amt <= 0) continue;
        const isIncome = entry.entry_type === "INCOME";
        const signed = isIncome ? amt : -amt;
        if (isIncome) {
          incomeDay += amt;
          totalIncome += amt;
        } else {
          outflowDay += amt;
          totalFixedOutflow += amt;
        }
        events.push({
          id: `entry-${entry.id}-${date}`,
          sourceId: entry.id,
          kind: entry.entry_type,
          title: entry.title,
          category: entry.category || "",
          amount: signed,
          frequency: entry.frequency,
          defaultDayHint: entryUsesDefaultDay(entry),
        });
      }
    }

    for (const ds of debtStates) {
      if (ds.remaining > 0.004 && ds.nextDue === date) {
        const payAmt =
          ds.paymentType === "FIXED_AMOUNT"
            ? ds.remaining
            : round2(Math.min(ds.remaining, ds.rate));
        if (payAmt > 0) {
          ds.remaining = round2(Math.max(0, ds.remaining - payAmt));
          outflowDay += payAmt;
          totalDebtPaid += payAmt;
          const paidOffToday = ds.remaining <= 0.004;
          if (paidOffToday) {
            ds.remaining = 0;
            debtsPaidOff.push({ id: ds.id, name: ds.name, date });
          }
          events.push({
            id: `debt-${ds.id}-${date}`,
            sourceId: ds.id,
            kind: ds.debtKind === "CREDIT" ? "CREDIT" : "DEBT",
            title: ds.name,
            amount: -payAmt,
            remainingAfter: ds.remaining,
            paidOffToday,
          });
        }

        if (ds.remaining > 0.004 && ds.paymentType === "INSTALLMENT" && ds.rate > 0) {
          ds.nextDue = addMonthsIso(date, 1, ds.dueDay);
        } else {
          ds.nextDue = null;
        }
      }
    }

    const extrasToday = extraByDate.get(date) || [];
    for (const ex of extrasToday) {
      const signed = round2(toNum(ex.amount));
      if (signed === 0) continue;
      if (signed > 0) {
        incomeDay += signed;
        totalIncome += signed;
      } else {
        outflowDay += Math.abs(signed);
        totalFixedOutflow += Math.abs(signed);
      }
      events.push({
        id: ex.id || `extra-${date}-${events.length}`,
        kind: ex.kind || (signed > 0 ? "INCOME" : "SIMULATED"),
        title: ex.title || "Simulation",
        amount: signed,
        simulated: true,
      });
    }

    const livingDed = dailyBudget;
    if (livingDed > 0) {
      totalLivingOutflow += livingDed;
    }

    const delta = round2(incomeDay - outflowDay - livingDed);
    runningBalance = round2(runningBalance + delta);

    if (runningBalance < minBalance) {
      minBalance = runningBalance;
      minBalanceDate = date;
    }
    if (runningBalance > maxBalance) {
      maxBalance = runningBalance;
      maxBalanceDate = date;
    }
    if (runningBalance < 0) {
      daysInNegative += 1;
      if (!firstNegativeDate) firstNegativeDate = date;
    }
    if (runningBalance < -dispoAvailable && !firstDispoBreachDate) {
      firstDispoBreachDate = date;
    }

    const remainingDebt = round2(debtStates.reduce((s, d) => s + d.remaining, 0));
    const netWorth = round2(runningBalance - remainingDebt - toNum(dispoUsed));

    let status = "SAFE";
    if (runningBalance < -dispoAvailable) {
      status = "CRITICAL";
    } else if (runningBalance < 0) {
      status = "NEGATIVE";
    } else if (bufferTarget > 0 ? runningBalance < bufferTarget : runningBalance < 100) {
      status = "TIGHT";
    }

    timeline.push({
      index: i,
      date,
      dayOfMonth: parts.day,
      monthKey: date.slice(0, 7),
      weekday: WEEKDAY_SHORT_DE[weekdayIdx],
      isToday: date === today,
      isWeekend: weekdayIdx >= 5,
      startBalance: startBal,
      incomeTotal: round2(incomeDay),
      outflowTotal: round2(outflowDay),
      livingDeduction: round2(livingDed),
      delta,
      endBalance: runningBalance,
      remainingDebt,
      netWorth,
      status,
      events,
    });
  }

  const endingDebt = timeline.length ? timeline[timeline.length - 1].remainingDebt : initialDebtTotal;

  return {
    startDateIso,
    endDateIso: timeline.length ? timeline[timeline.length - 1].date : startDateIso,
    daysCount: horizon,
    startingBalance: round2(toNum(startingBalance)),
    endingBalance: runningBalance,
    netChange: round2(runningBalance - toNum(startingBalance)),
    minBalance,
    minBalanceDate,
    maxBalance,
    maxBalanceDate,
    firstNegativeDate,
    firstDispoBreachDate,
    daysInNegative,
    totalIncome: round2(totalIncome),
    totalFixedOutflow: round2(totalFixedOutflow),
    totalDebtPaid: round2(totalDebtPaid),
    totalLivingOutflow: round2(totalLivingOutflow),
    startingDebt: initialDebtTotal,
    endingDebt,
    debtReducedBy: round2(initialDebtTotal - endingDebt),
    debtsPaidOff,
    overdueDebts,
    timeline,
  };
}

/**
 * Date A -> Date B Safe-to-Spend Daily Budget & Savings Calculator
 * Includes exact mid-period Cashflow Bottleneck detection!
 */
export function calculatePeriodSimulator({
  startDateIso = todayIso(),
  endDateIso = addDaysIso(todayIso(), 29),
  startingMoney = 0,
  extraIncome = 0,
  entries = [],
  debts = [],
  includeScheduled = true,
  disabledOccurrenceKeys = new Set(),
  savingsMode = "AMOUNT", // "AMOUNT" | "PERCENT" | "DAILY" | "TARGET_END"
  savingsValue = 0,
  safetyFloor = 0,
  testDailySpend = null,
} = {}) {
  const safeEnd = endDateIso >= startDateIso ? endDateIso : startDateIso;
  const totalDays = diffDaysInclusive(startDateIso, safeEnd);
  const startCash = round2(toNum(startingMoney));
  const bonusCash = round2(toNum(extraIncome));
  const floor = round2(Math.max(0, toNum(safetyFloor)));

  // Run a 0-living-budget baseline timeline to gather all scheduled occurrences in [A..B]
  const rawSim = simulateDailyTimeline({
    startDateIso,
    days: totalDays,
    startingBalance: startCash,
    entries: includeScheduled ? entries : [],
    debts: includeScheduled ? debts : [],
    includeDailyBudget: false,
  });

  const occurrences = [];
  for (const day of rawSim.timeline) {
    for (const ev of day.events) {
      const key = `${ev.id}`;
      const enabled = !disabledOccurrenceKeys.has(key);
      occurrences.push({
        key,
        date: day.date,
        title: ev.title,
        kind: ev.kind,
        amount: ev.amount,
        enabled,
      });
    }
  }

  // Reconstruct daily cumulative curve B_0(k) for k = 1..totalDays using only enabled occurrences
  const occByDate = new Map();
  for (const occ of occurrences) {
    if (!occ.enabled) continue;
    if (!occByDate.has(occ.date)) occByDate.set(occ.date, 0);
    occByDate.set(occ.date, occByDate.get(occ.date) + occ.amount);
  }

  let scheduledIncome = 0;
  let scheduledOutflow = 0;
  for (const occ of occurrences) {
    if (!occ.enabled) continue;
    if (occ.amount > 0) scheduledIncome += occ.amount;
    else scheduledOutflow += Math.abs(occ.amount);
  }
  scheduledIncome = round2(scheduledIncome);
  scheduledOutflow = round2(scheduledOutflow);

  let cumBalance = round2(startCash + bonusCash);
  const b0Curve = [];
  let bottleneckDailyMax = Infinity;
  let bottleneckDate = null;
  let bottleneckBalanceBeforeSpend = cumBalance;

  for (let k = 1; k <= totalDays; k++) {
    const d = addDaysIso(startDateIso, k - 1);
    const dayNet = occByDate.get(d) || 0;
    cumBalance = round2(cumBalance + dayNet);
    b0Curve.push({ dayNumber: k, date: d, balanceZeroSpend: cumBalance });

    const maxDailyUntilK = (cumBalance - floor) / k;
    if (maxDailyUntilK < bottleneckDailyMax) {
      bottleneckDailyMax = maxDailyUntilK;
      bottleneckDate = d;
      bottleneckBalanceBeforeSpend = cumBalance;
    }
  }

  const endPoolBeforeSavings = cumBalance; // startCash + bonusCash + scheduledIncome - scheduledOutflow
  const spendableAboveFloor = endPoolBeforeSavings - floor;

  let plannedSavings = 0;
  const sVal = Math.max(0, toNum(savingsValue));
  if (savingsMode === "AMOUNT") {
    plannedSavings = round2(sVal);
  } else if (savingsMode === "PERCENT") {
    const pct = Math.min(100, sVal);
    plannedSavings = round2(Math.max(0, spendableAboveFloor) * (pct / 100));
  } else if (savingsMode === "DAILY") {
    plannedSavings = round2(sVal * totalDays);
  } else if (savingsMode === "TARGET_END") {
    // User wants at least sVal remaining at endDateIso total
    plannedSavings = round2(Math.max(0, sVal - floor));
  }

  const totalNetSpendable = round2(spendableAboveFloor - plannedSavings);
  const theoreticalDailyBudget = round2(totalNetSpendable / totalDays);
  const theoreticalWeeklyBudget = round2(theoreticalDailyBudget * 7);

  const safeDailyBudgetRaw = Math.min(theoreticalDailyBudget, bottleneckDailyMax);
  const safeDailyBudget = round2(safeDailyBudgetRaw);
  const hasMidPeriodBottleneck =
    bottleneckDate &&
    bottleneckDate < safeEnd &&
    safeDailyBudget + 0.05 < theoreticalDailyBudget;

  // Reverse calculation: if user spends `customDaily` per day, what happens?
  const chosenDaily =
    testDailySpend !== null && testDailySpend !== undefined && testDailySpend !== ""
      ? Math.max(0, toNum(testDailySpend))
      : Math.max(0, theoreticalDailyBudget);

  const totalChosenSpend = round2(chosenDaily * totalDays);
  const projectedEndBalanceWithChosen = round2(endPoolBeforeSavings - totalChosenSpend);
  const extraSavedVsZero = round2(projectedEndBalanceWithChosen - floor);
  let minBalanceWithChosen = Infinity;
  let minDateWithChosen = startDateIso;
  for (const pt of b0Curve) {
    const balAtK = round2(pt.balanceZeroSpend - pt.dayNumber * chosenDaily);
    if (balAtK < minBalanceWithChosen) {
      minBalanceWithChosen = balAtK;
      minDateWithChosen = pt.date;
    }
  }

  return {
    startDateIso,
    endDateIso: safeEnd,
    totalDays,
    startingMoney: startCash,
    extraIncome: bonusCash,
    scheduledIncome,
    scheduledOutflow,
    endPoolBeforeSavings,
    safetyFloor: floor,
    plannedSavings,
    totalNetSpendable,
    theoreticalDailyBudget,
    theoreticalWeeklyBudget,
    safeDailyBudget,
    safeWeeklyBudget: round2(safeDailyBudget * 7),
    hasMidPeriodBottleneck,
    bottleneckDate,
    bottleneckBalanceBeforeSpend,
    occurrences,
    reverseCheck: {
      dailySpend: round2(chosenDaily),
      totalSpend: totalChosenSpend,
      projectedEndBalance: projectedEndBalanceWithChosen,
      projectedSavingsAboveFloor: extraSavedVsZero,
      minBalanceDuringPeriod: minBalanceWithChosen === Infinity ? startCash : minBalanceWithChosen,
      minBalanceDate: minDateWithChosen,
    },
  };
}

/**
 * Helper to compute monthly equivalent of a FinanceEntry in a given YYYY-MM month.
 */
function calcEntryAmountInMonth(entry, ymStr) {
  if (!entry || entry.is_active === false) return 0;
  const amt = Math.max(0, toNum(entry.amount));
  if (amt <= 0) return 0;

  const year = Number.parseInt(ymStr.slice(0, 4), 10);
  const month = Number.parseInt(ymStr.slice(5, 7), 10);
  const monthEndIso = safeIsoDate(year, month, 31);
  const freq = entry.frequency || "MONTHLY";

  if (freq === "ONCE") {
    return entry.due_date && entry.due_date.slice(0, 7) === ymStr ? amt : 0;
  }
  if (entry.due_date && entry.due_date > monthEndIso) {
    return 0;
  }
  if (freq === "MONTHLY") {
    return amt;
  }
  if (freq === "WEEKLY") {
    return round2((amt * 52) / 12);
  }
  if (freq === "YEARLY") {
    if (entry.due_date) {
      const dp = parseIsoParts(entry.due_date);
      if (dp && dp.month === month) return amt;
      return 0;
    }
    return month === 1 ? amt : 0;
  }
  return 0;
}

/**
 * Long-Term Debt Payoff & Wealth Roadmap Engine (12–120 months)
 * Supports:
 *  - "CURRENT": Standard contract rates (when a debt finishes, rate drops off and increases monthly cashflow!)
 *  - "SNOWBALL": Smallest remaining balance first + freed-up rates roll over into next debt!
 *  - "PRESSURE": Highest rate-to-balance pressure first + freed-up rates roll over into next debt!
 */
export function simulateLongTermRoadmap({
  startMonthYm = currentMonthIso(),
  horizonMonths = 24,
  startingBalance = 0,
  startingSavings = 0,
  dispoUsed = 0,
  monthlySavingsTarget = 0,
  dailyLivingBudget = 0,
  includeLivingBudget = true,
  entries = [],
  debts = [],
  strategy = "CURRENT", // "CURRENT" | "SNOWBALL" | "PRESSURE"
  extraMonthlyDebtBudget = 0,
  disabledEntryIds = new Set(),
} = {}) {
  const maxScanMonths = Math.max(horizonMonths, 120);
  const activeEntries = (entries || []).filter(
    (e) => e && e.is_active !== false && !disabledEntryIds.has(e.id)
  );

  // Clone active debts
  const simDebts = (debts || [])
    .filter((d) => d && d.status === "ACTIVE" && !d.is_fully_paid)
    .map((d) => {
      const rem = round2(Math.max(0, toNum(d.total_amount) - toNum(d.amount_paid)));
      const pType = d.payment_type || "INSTALLMENT";
      const minRate = pType === "FIXED_AMOUNT" ? rem : round2(Math.max(0, toNum(d.monthly_payment)));
      const startYm = d.start_date ? d.start_date.slice(0, 7) : startMonthYm;
      const dueYm = d.next_due_date ? d.next_due_date.slice(0, 7) : startYm;
      return {
        id: d.id,
        name: d.name,
        debtKind: d.debt_kind || "DEBT",
        paymentType: pType,
        initialRemaining: rem,
        remaining: rem,
        minRate,
        activeFromYm: pType === "FIXED_AMOUNT" ? dueYm : startYm,
        paidOffYm: null,
        monthsToPayOff: null,
      };
    })
    .filter((d) => d.remaining > 0);

  const initialDebtTotal = round2(simDebts.reduce((s, d) => s + d.remaining, 0));
  const baseMonthlyDebtPool = round2(
    simDebts.filter((d) => d.paymentType === "INSTALLMENT").reduce((s, d) => s + d.minRate, 0)
  );
  const extraBoost = round2(Math.max(0, toNum(extraMonthlyDebtBudget)));
  const useRollover = strategy === "SNOWBALL" || strategy === "PRESSURE" || extraBoost > 0;

  let runningBalance = round2(toNum(startingBalance));
  let runningSavings = round2(toNum(startingSavings));
  const fixedSavingsGoalPerMonth = round2(Math.max(0, toNum(monthlySavingsTarget)));

  let debtFreeMonth = initialDebtTotal <= 0 ? startMonthYm : null;
  let monthsUntilDebtFree = initialDebtTotal <= 0 ? 0 : null;

  const initialNetWorth = round2(runningBalance + runningSavings - initialDebtTotal - toNum(dispoUsed));
  let breakEvenMonth = initialNetWorth >= 0 ? startMonthYm : null;
  let monthsUntilBreakEven = initialNetWorth >= 0 ? 0 : null;

  const months = [];

  for (let mIdx = 0; mIdx < maxScanMonths; mIdx++) {
    const ym = addMonthsYm(startMonthYm, mIdx);
    const year = Number.parseInt(ym.slice(0, 4), 10);
    const month = Number.parseInt(ym.slice(5, 7), 10);
    const mDays = daysInMonth(year, month);

    let income = 0;
    let fixedCosts = 0;
    let subscriptions = 0;
    let plannedOnce = 0;
    let entrySavings = 0;

    for (const entry of activeEntries) {
      const val = calcEntryAmountInMonth(entry, ym);
      if (val <= 0) continue;
      if (entry.entry_type === "INCOME") {
        income += val;
      } else if (entry.entry_type === "SAVING") {
        entrySavings += val;
      } else if (entry.entry_type === "SUBSCRIPTION") {
        subscriptions += val;
      } else if (entry.frequency === "ONCE") {
        plannedOnce += val;
      } else {
        fixedCosts += val;
      }
    }

    const livingCosts = includeLivingBudget ? round2(Math.max(0, toNum(dailyLivingBudget)) * mDays) : 0;

    // Debt amortization for this month
    let monthDebtPaid = 0;
    const paidOffThisMonth = [];
    const eligibleDebts = simDebts.filter((d) => d.remaining > 0.004 && d.activeFromYm <= ym);

    // 1) Pay mandatory minimums first
    for (const d of eligibleDebts) {
      const mandatory = d.paymentType === "FIXED_AMOUNT" ? d.remaining : Math.min(d.remaining, d.minRate);
      if (mandatory > 0) {
        d.remaining = round2(Math.max(0, d.remaining - mandatory));
        monthDebtPaid += mandatory;
        if (d.remaining <= 0.004) {
          d.remaining = 0;
          d.paidOffYm = ym;
          d.monthsToPayOff = mIdx + 1;
          paidOffThisMonth.push(d.name);
        }
      }
    }

    // 2) Apply rollover + extra boost if active
    if (useRollover) {
      const targetPool = baseMonthlyDebtPool + extraBoost;
      let extraAvailable = round2(Math.max(0, targetPool - monthDebtPaid));

      if (extraAvailable > 0) {
        const openTargets = simDebts.filter((d) => d.remaining > 0.004 && d.activeFromYm <= ym);
        if (strategy === "PRESSURE") {
          openTargets.sort((a, b) => {
            const pA = a.remaining > 0 ? a.minRate / a.remaining : 0;
            const pB = b.remaining > 0 ? b.minRate / b.remaining : 0;
            return pB - pA || a.remaining - b.remaining;
          });
        } else {
          // Default SNOWBALL: smallest remaining balance first
          openTargets.sort((a, b) => a.remaining - b.remaining || b.minRate - a.minRate);
        }

        for (const target of openTargets) {
          if (extraAvailable <= 0.004) break;
          const topUp = round2(Math.min(target.remaining, extraAvailable));
          if (topUp > 0) {
            target.remaining = round2(Math.max(0, target.remaining - topUp));
            monthDebtPaid += topUp;
            extraAvailable = round2(extraAvailable - topUp);
            if (target.remaining <= 0.004) {
              target.remaining = 0;
              target.paidOffYm = ym;
              target.monthsToPayOff = mIdx + 1;
              if (!paidOffThisMonth.includes(target.name)) {
                paidOffThisMonth.push(target.name);
              }
            }
          }
        }
      }
    }

    monthDebtPaid = round2(monthDebtPaid);
    const savingsContribution = round2(entrySavings + fixedSavingsGoalPerMonth);
    const totalOutflow = round2(fixedCosts + subscriptions + plannedOnce + livingCosts + monthDebtPaid + savingsContribution);
    const netCashflow = round2(income - totalOutflow);

    runningBalance = round2(runningBalance + netCashflow);
    runningSavings = round2(runningSavings + savingsContribution);
    const remainingDebt = round2(simDebts.reduce((s, d) => s + d.remaining, 0));
    const netWorth = round2(runningBalance + runningSavings - remainingDebt - toNum(dispoUsed));

    if (!debtFreeMonth && remainingDebt <= 0.004) {
      debtFreeMonth = ym;
      monthsUntilDebtFree = mIdx + 1;
    }
    if (!breakEvenMonth && netWorth >= 0) {
      breakEvenMonth = ym;
      monthsUntilBreakEven = mIdx + 1;
    }

    if (mIdx < horizonMonths) {
      months.push({
        index: mIdx,
        monthKey: ym,
        label: formatMonthYearDe(ym, true),
        fullLabel: formatMonthYearDe(ym, false),
        income: round2(income),
        fixedCosts: round2(fixedCosts),
        subscriptions: round2(subscriptions),
        plannedOnce: round2(plannedOnce),
        livingCosts: round2(livingCosts),
        debtPayment: monthDebtPaid,
        savingsContribution,
        totalOutflow,
        netCashflow,
        endingBalance: runningBalance,
        totalSavings: runningSavings,
        remainingDebt,
        netWorth,
        paidOffDebts: paidOffThisMonth,
      });
    }
  }

  const payoffSchedule = simDebts
    .map((d) => ({
      id: d.id,
      name: d.name,
      debtKind: d.debtKind,
      initialRemaining: d.initialRemaining,
      minRate: d.minRate,
      paidOffYm: d.paidOffYm,
      paidOffLabel: d.paidOffYm ? formatMonthYearDe(d.paidOffYm, false) : "Offen (> 10 J.)",
      monthsToPayOff: d.monthsToPayOff,
    }))
    .sort((a, b) => (a.monthsToPayOff ?? 999) - (b.monthsToPayOff ?? 999));

  const endSnap = months.length ? months[months.length - 1] : null;

  return {
    strategy,
    horizonMonths,
    initialDebtTotal,
    initialNetWorth,
    debtFreeMonth,
    debtFreeLabel: debtFreeMonth ? formatMonthYearDe(debtFreeMonth, false) : "Noch offen (Rate prüfen)",
    monthsUntilDebtFree,
    breakEvenMonth,
    breakEvenLabel: breakEvenMonth ? formatMonthYearDe(breakEvenMonth, false) : "Außerhalb Horizont",
    monthsUntilBreakEven,
    horizonEndBalance: endSnap ? endSnap.endingBalance : runningBalance,
    horizonEndSavings: endSnap ? endSnap.totalSavings : runningSavings,
    horizonEndDebt: endSnap ? endSnap.remainingDebt : 0,
    horizonEndNetWorth: endSnap ? endSnap.netWorth : initialNetWorth,
    payoffSchedule,
    months,
  };
}

/**
 * Evaluates whether a planned purchase (one-time or installment) is safe within a 90-day daily timeline.
 */
export function evaluatePurchaseSafety({
  amount = 0,
  purchaseDateIso = todayIso(),
  installments = 1,
  title = "Geplanter Kauf",
  startingBalance = 0,
  dispoLimit = 0,
  dispoUsed = 0,
  emergencyBuffer = 0,
  dailyLivingBudget = 0,
  includeDailyBudget = true,
  entries = [],
  debts = [],
} = {}) {
  const totalCost = round2(Math.max(0, toNum(amount)));
  const partsCount = Math.max(1, Math.min(24, Number.parseInt(installments, 10) || 1));
  const startIso = todayIso();

  const baseline = simulateDailyTimeline({
    startDateIso: startIso,
    days: 90,
    startingBalance,
    dispoLimit,
    dispoUsed,
    emergencyBuffer,
    entries,
    debts,
    includeDailyBudget,
    dailyLivingBudget,
  });

  const buildExtraEvents = (anchorDateIso) => {
    const evs = [];
    const perPart = round2(totalCost / partsCount);
    const pDay = parseIsoParts(anchorDateIso)?.day || 1;
    for (let i = 0; i < partsCount; i++) {
      const d = i === 0 ? anchorDateIso : addMonthsIso(anchorDateIso, i, pDay);
      const partAmt = i === partsCount - 1 ? round2(totalCost - perPart * (partsCount - 1)) : perPart;
      evs.push({
        date: d,
        amount: -partAmt,
        title: partsCount > 1 ? `${title} (Rate ${i + 1}/${partsCount})` : title,
        kind: "SIMULATED",
      });
    }
    return evs;
  };

  const withPurchase = simulateDailyTimeline({
    startDateIso: startIso,
    days: 90,
    startingBalance,
    dispoLimit,
    dispoUsed,
    emergencyBuffer,
    entries,
    debts,
    includeDailyBudget,
    dailyLivingBudget,
    extraEvents: totalCost > 0 ? buildExtraEvents(purchaseDateIso) : [],
  });

  const floor = Math.max(0, toNum(emergencyBuffer));
  let verdict = "SAFE"; // SAFE | TIGHT | DANGER
  if (withPurchase.minBalance < 0) {
    verdict = "DANGER";
  } else if (withPurchase.minBalance < Math.max(floor, 75)) {
    verdict = "TIGHT";
  }

  // If not SAFE on purchaseDateIso, scan up to 60 days ahead for earliest SAFE date
  let earliestSafeDate = verdict === "SAFE" ? purchaseDateIso : null;
  if (verdict !== "SAFE" && totalCost > 0) {
    for (let offset = 1; offset <= 60; offset++) {
      const candidateDate = addDaysIso(startIso, offset);
      if (candidateDate <= purchaseDateIso) continue;
      const testSim = simulateDailyTimeline({
        startDateIso: startIso,
        days: 90,
        startingBalance,
        dispoLimit,
        dispoUsed,
        emergencyBuffer,
        entries,
        debts,
        includeDailyBudget,
        dailyLivingBudget,
        extraEvents: buildExtraEvents(candidateDate),
      });
      if (testSim.minBalance >= Math.max(floor, 50) && testSim.minBalance >= 0) {
        earliestSafeDate = candidateDate;
        break;
      }
    }
  }

  return {
    totalCost,
    installments: partsCount,
    installmentAmount: round2(totalCost / partsCount),
    verdict,
    baselineMinBalance: baseline.minBalance,
    afterMinBalance: withPurchase.minBalance,
    afterMinBalanceDate: withPurchase.minBalanceDate,
    afterEndingBalance: withPurchase.endingBalance,
    dailyBudgetImpact30d: round2(-(totalCost / Math.max(1, partsCount)) / 30),
    earliestSafeDate,
  };
}

