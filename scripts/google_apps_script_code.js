/**
 * INDULGE GLOBAL — LUXURY CONCIERGE LEAD INTELLIGENCE & CALL DISPOSITION CRM
 * ============================================================================
 * Google Apps Script Webhook & Sheet CRM for Real-Time Lead Ingestion,
 * SDR Cold Calling, Call Outcome Tapping & Dual-Corridor Tracking.
 * 
 * SETUP INSTRUCTIONS (Takes 60 seconds):
 * 1. Create a new Google Sheet (or open an existing one).
 * 2. Click "Extensions" -> "Apps Script".
 * 3. Delete any default code in Code.gs and PASTE THIS ENTIRE FILE.
 * 4. Click "Deploy" (top right) -> "New deployment".
 * 5. Select type: "Web app".
 * 6. Set Description: "Indulge Global Real-Time Lead CRM".
 * 7. Set "Execute as": "Me" (your email).
 * 8. Set "Who has access": "Anyone". (CRITICAL so the Python server can POST leads).
 * 9. Click "Deploy" and COPY the "Web app URL" (starts with https://script.google.com/macros/s/.../exec).
 * 10. Paste the URL into your Indulge Global Dashboard or .env file (GOOGLE_SHEET_WEBHOOK_URL).
 */

const SHEET_NAME = "Indulge Global HNI Funnel";

// Column Definitions
const COLUMNS = [
  { header: "Call Disposition / Status", width: 220 },       // A: SDR Status Dropdown
  { header: "Call Outcome & Notes", width: 280 },            // B: SDR Call Notes
  { header: "Tapped By (SDR)", width: 130 },                 // C: SDR Name
  { header: "Last Contact Date", width: 130 },               // D: Timestamp
  { header: "Follow-Up Date", width: 120 },                  // E: Follow-up Date
  { header: "First Name", width: 120 },                      // F
  { header: "Last Name", width: 120 },                       // G
  { header: "Role / Executive Title", width: 220 },          // H
  { header: "Company / Enterprise", width: 200 },            // I
  { header: "Phone Number (Formatted)", width: 160 },        // J
  { header: "Direct E.164 (VoIP/Click-to-Call)", width: 160 },// K (Dedup key)
  { header: "WhatsApp Click-to-Chat", width: 170 },          // L
  { header: "Email Address", width: 220 },                   // M
  { header: "Deliverability (Azure AD)", width: 150 },       // N
  { header: "City / Country", width: 160 },                  // O
  { header: "NRI Corridor / Wealth Hub", width: 240 },       // P
  { header: "Wealth Signal / Equity Tier", width: 260 },     // Q
  { header: "Indulge Pitch Angle", width: 300 },             // R
  { header: "Dual-Corridor Outreach Script", width: 360 },   // S
  { header: "Source / Registry", width: 200 },               // T
  { header: "Ingested At", width: 140 }                      // U
];

const DISPOSITIONS = [
  "✨ New Lead (Untapped)",
  "🟢 Call Picked - Interested (VIP)",
  "⭐ Meeting / Presentation Booked",
  "💬 WhatsApp Sent & Engaging",
  "📞 Call Scheduled",
  "⏳ Ringing / No Answer (Try Later)",
  "🔄 Busy / Callback Requested",
  "❌ Not Interested / Disqualified",
  "🚫 Wrong Number / Gatekeeper Block"
];

/**
 * Handle incoming GET requests (Health check and status)
 */
function doGet(e) {
  var sheet = getOrCreateSheet();
  var lastRow = Math.max(sheet.getLastRow(), 1);
  var totalLeads = lastRow > 1 ? lastRow - 1 : 0;
  
  return ContentService.createTextOutput(JSON.stringify({
    status: "online",
    message: "Indulge Global Real-Time Google Sheet CRM Webhook is active and listening.",
    total_leads_in_sheet: totalLeads,
    timestamp: new Date().toISOString()
  })).setMimeType(ContentService.MimeType.JSON);
}

/**
 * Handle incoming POST requests from Python backend
 * Expects JSON payload:
 * { "action": "sync_leads", "leads": [ ... ] }
 * or
 * { "action": "add_lead", "lead": { ... } }
 */
function doPost(e) {
  try {
    var payload;
    if (e.postData && e.postData.contents) {
      payload = JSON.parse(e.postData.contents);
    } else {
      payload = e.parameter || {};
    }

    var sheet = getOrCreateSheet();
    var leads = [];

    if (payload.leads && Array.isArray(payload.leads)) {
      leads = payload.leads;
    } else if (payload.lead && typeof payload.lead === "object") {
      leads = [payload.lead];
    } else if (Array.isArray(payload)) {
      leads = payload;
    }

    if (leads.length === 0) {
      return ContentService.createTextOutput(JSON.stringify({
        status: "warning",
        message: "No leads provided in payload."
      })).setMimeType(ContentService.MimeType.JSON);
    }

    var result = upsertLeads(sheet, leads);

    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      added: result.added,
      updated: result.updated,
      total_leads: result.total,
      timestamp: new Date().toISOString()
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: err.toString(),
      stack: err.stack
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Get or create the dedicated CRM sheet and apply styling
 */
function getOrCreateSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME, 0);
    formatSheetHeaders(sheet);
  } else {
    // Check if headers match
    if (sheet.getLastRow() === 0) {
      formatSheetHeaders(sheet);
    }
  }
  return sheet;
}

/**
 * Apply headers, styling, dropdown validation, and colors
 */
function formatSheetHeaders(sheet) {
  var headerValues = [COLUMNS.map(function(c) { return c.header; })];
  
  sheet.getRange(1, 1, 1, COLUMNS.length).setValues(headerValues);
  
  // Luxury Styling for Header: Navy #0F172A + White Bold Text
  var headerRange = sheet.getRange(1, 1, 1, COLUMNS.length);
  headerRange.setBackground("#0F172A")
             .setFontColor("#FFFFFF")
             .setFontWeight("bold")
             .setFontSize(10)
             .setFontFamily("Plus Jakarta Sans")
             .setVerticalAlignment("middle")
             .setWrap(false);
             
  sheet.setRowHeight(1, 38);
  sheet.setFrozenRows(1);
  sheet.setFrozenColumns(2); // Freeze Status and Notes

  // Set column widths
  for (var i = 0; i < COLUMNS.length; i++) {
    sheet.setColumnWidth(i + 1, COLUMNS[i].width);
  }

  // Set data validation for Column A (Call Disposition)
  var rule = SpreadsheetApp.newDataValidation()
    .requireValueInList(DISPOSITIONS, true)
    .setAllowInvalid(false)
    .build();
  sheet.getRange("A2:A10000").setDataValidation(rule);

  // Apply conditional formatting colors to Call Disposition (Column A)
  setupConditionalFormatting(sheet);
}

/**
 * Setup conditional formatting rules for SDR Tapping Status
 */
function setupConditionalFormatting(sheet) {
  sheet.clearConditionalFormatRules();
  var range = sheet.getRange("A2:A10000");
  
  var rules = [
    // VIP Interested -> Emerald Green
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextContains("Call Picked - Interested (VIP)")
      .setBackground("#D1FAE5")
      .setFontColor("#065F46")
      .setRanges([range])
      .build(),
      
    // Meeting Booked -> Amber / Gold
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextContains("Meeting / Presentation Booked")
      .setBackground("#FEF3C7")
      .setFontColor("#92400E")
      .setRanges([range])
      .build(),

    // WhatsApp Sent -> Sky Blue
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextContains("WhatsApp Sent & Engaging")
      .setBackground("#E0F2FE")
      .setFontColor("#075985")
      .setRanges([range])
      .build(),

    // Call Scheduled -> Violet
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextContains("Call Scheduled")
      .setBackground("#EDE9FE")
      .setFontColor("#5B21B6")
      .setRanges([range])
      .build(),

    // Ringing / No Answer -> Light Slate
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextContains("Ringing / No Answer (Try Later)")
      .setBackground("#F3F4F6")
      .setFontColor("#4B5563")
      .setRanges([range])
      .build(),

    // Busy / Callback -> Light Yellow
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextContains("Busy / Callback Requested")
      .setBackground("#FEF9C3")
      .setFontColor("#854D0E")
      .setRanges([range])
      .build(),

    // Not Interested -> Light Red
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextContains("Not Interested / Disqualified")
      .setBackground("#FEE2E2")
      .setFontColor("#991B1B")
      .setRanges([range])
      .build(),

    // Wrong Number -> Rose
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextContains("Wrong Number / Gatekeeper Block")
      .setBackground("#FFE4E6")
      .setFontColor("#9F1239")
      .setRanges([range])
      .build(),

    // New Lead -> Subtle Slate Blue
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextContains("New Lead (Untapped)")
      .setBackground("#F8FAFC")
      .setFontColor("#475569")
      .setRanges([range])
      .build()
  ];

  sheet.setConditionalFormatRules(rules);
}

/**
 * Non-destructive Upsert:
 * - Deduplicates by Direct E.164 (Column K) or Email (Column M) or Full Name (F + G).
 * - CRITICAL: If row already exists, PRESERVES existing Column A (Status), Column B (Notes),
 *   Column C (SDR), Column D (Last Contact Date), and Column E (Follow-Up Date)!
 */
function upsertLeads(sheet, leads) {
  var lastRow = sheet.getLastRow();
  var existingMap = {}; // key -> rowIndex (1-based)
  
  if (lastRow > 1) {
    // Read existing keys: E.164 (Col K = 11), Email (Col M = 13), Name (Col F=6, Col G=7)
    var numRows = lastRow - 1;
    var keysRange = sheet.getRange(2, 6, numRows, 8).getValues(); // Cols F to M
    for (var r = 0; r < keysRange.length; r++) {
      var rowIdx = r + 2;
      var fn = String(keysRange[r][0] || "").trim().toLowerCase();
      var ln = String(keysRange[r][1] || "").trim().toLowerCase();
      var e164 = String(keysRange[r][5] || "").replace(/[^\d+]/g, ""); // Col K is offset 5 from Col F
      var email = String(keysRange[r][7] || "").trim().toLowerCase();   // Col M is offset 7 from Col F
      
      if (e164) existingMap[e164] = rowIdx;
      if (email && email !== "n/a") existingMap[email] = rowIdx;
      if (fn && ln) existingMap[fn + "_" + ln] = rowIdx;
    }
  }

  var newRows = [];
  var updatedCount = 0;
  var nowStr = Utilities.formatDate(new Date(), Session.getScriptTimeZone() || "GMT", "yyyy-MM-dd HH:mm");

  for (var i = 0; i < leads.length; i++) {
    var l = leads[i];
    var fn = String(l["First Name"] || "").trim();
    var ln = String(l["Last Name"] || "").trim();
    var e164 = String(l["E164"] || l["Phone Number"] || "").replace(/[^\d+]/g, "");
    var email = String(l["Email"] || "").trim();
    var phone = String(l["Phone Number"] || e164 || "");
    var phoneType = String(l["Phone Type"] || "VIP Personal Mobile");
    var waLink = String(l["WhatsApp Link"] || "");
    var dualCopy = String(l["Dual Corridor Copy"] || "");
    var cleanDigits = e164.replace(/[^\d]/g, "");
    
    // Build direct click-to-chat WhatsApp formula
    var waFormula = "";
    if (cleanDigits) {
      var targetUrl = waLink || ("https://wa.me/" + cleanDigits + (dualCopy ? "?text=" + encodeURIComponent(dualCopy) : ""));
      waFormula = '=HYPERLINK("' + targetUrl + '", "💬 WhatsApp Chat")';
    } else {
      waFormula = "—";
    }

    var existingRow = null;
    if (e164 && existingMap[e164]) existingRow = existingMap[e164];
    else if (email && email.toLowerCase() !== "n/a" && existingMap[email.toLowerCase()]) existingRow = existingMap[email.toLowerCase()];
    else if (fn && ln && existingMap[fn.toLowerCase() + "_" + ln.toLowerCase()]) existingRow = existingMap[fn.toLowerCase() + "_" + ln.toLowerCase()];

    var metaCols = [
      fn,                                              // F: First Name
      ln,                                              // G: Last Name
      String(l["Role"] || "Chairman / Principal"),      // H: Role
      String(l["Company"] || "Private Enterprise"),     // I: Company
      phone,                                           // J: Formatted Phone
      e164,                                            // K: E.164
      waFormula,                                       // L: WhatsApp Clickable Link
      email || "N/A",                                  // M: Email
      String(l["Deliverability Status"] || "Verified"),// N: Deliverability
      String(l["City/Country"] || ""),                 // O: City/Country
      String(l["NRI Corridor"] || ""),                 // P: NRI Corridor
      String(l["Wealth Signal"] || ""),                // Q: Wealth Signal
      String(l["Pitch Angle"] || ""),                  // R: Pitch Angle
      dualCopy,                                        // S: Dual-Corridor Copy
      String(l["Source"] || "Verified Registry"),      // T: Source
      nowStr                                           // U: Ingested At
    ];

    if (existingRow) {
      // Non-destructive update: Update ONLY columns F through U.
      // LEAVE Columns A to E (Status, Notes, SDR, Timestamps) 100% UNTOUCHED!
      sheet.getRange(existingRow, 6, 1, metaCols.length).setValues([metaCols]);
      updatedCount++;
    } else {
      // New row: Initialize default status "✨ New Lead (Untapped)"
      var fullNewRow = [
        "✨ New Lead (Untapped)", // A: Call Disposition
        "",                       // B: Call Outcome & Notes
        "",                       // C: Tapped By (SDR)
        "",                       // D: Last Contact Date
        "",                       // E: Follow-Up Date
      ].concat(metaCols);

      newRows.push(fullNewRow);

      // Register key in map so we don't duplicate within same payload
      if (e164) existingMap[e164] = lastRow + newRows.length;
      if (email && email.toLowerCase() !== "n/a") existingMap[email.toLowerCase()] = lastRow + newRows.length;
      if (fn && ln) existingMap[fn.toLowerCase() + "_" + ln.toLowerCase()] = lastRow + newRows.length;
    }
  }

  if (newRows.length > 0) {
    var insertStart = sheet.getLastRow() + 1;
    var range = sheet.getRange(insertStart, 1, newRows.length, COLUMNS.length);
    range.setValues(newRows);
    
    // Style new rows with clean font & height
    range.setFontFamily("Plus Jakarta Sans")
         .setFontSize(9)
         .setVerticalAlignment("middle");
         
    // Set notes & pitch wrap
    sheet.getRange(insertStart, 2, newRows.length, 1).setWrap(true);  // Notes wrap
    sheet.getRange(insertStart, 18, newRows.length, 2).setWrap(true); // Pitch & Copy wrap
  }

  var finalTotal = Math.max(sheet.getLastRow() - 1, 0);
  return { added: newRows.length, updated: updatedCount, total: finalTotal };
}

/**
 * Custom Menu for Google Sheets
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("💎 Indulge Global CRM")
    .addItem("📊 Re-Apply Formatting & Dropdowns", "menuReformat")
    .addItem("ℹ️ Webhook Connection Info", "menuWebhookInfo")
    .addToUi();
}

function menuReformat() {
  var sheet = getOrCreateSheet();
  formatSheetHeaders(sheet);
  SpreadsheetApp.getActiveSpreadsheet().toast("Indulge Global CRM headers & status dropdowns reformatted successfully!", "Success", 5);
}

function menuWebhookInfo() {
  SpreadsheetApp.getUi().alert(
    "Indulge Global CRM Webhook Active\n\n" +
    "1. Deploy as Web App -> Execute as: Me -> Who has access: Anyone.\n" +
    "2. Copy the web app URL into your Python dashboard or .env file as GOOGLE_SHEET_WEBHOOK_URL.\n" +
    "3. Any leads mined in the dashboard will instantly reflect here in real-time without overwriting your call notes!"
  );
}
