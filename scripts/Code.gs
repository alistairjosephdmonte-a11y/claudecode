// ===== CONFIGURATION =====

var CONFIG = {
  MAIN_SHEET: 'Pipeline',
  DASHBOARD_SHEET: 'Dashboard',
  CLOSED_SHEET: 'Closed Deals',
  ACTIVE_SHEET: 'Active Pipeline',
  LOST_SHEET: 'Lost Deals',
  HEADER_ROW: 1,
  COL: {
    DATE: 1,
    BRAND: 2,
    SCOPE: 3,
    HANDLER: 4,
    POC: 5,
    PHONE: 6,
    EMAIL: 7,
    STAGE: 8,
    COSTS: 9,
    FOLLOWUP: 10,
    STATUS: 11
  },
  STAGES: ['First Call', 'Pitch', 'Commercials', 'Closed', 'Didnt work out'],
  ACTIVE_STAGES: ['First Call', 'Pitch', 'Commercials'],
  HANDLERS: ['Tan', 'Ally'],
  SCOPES: ['Branding', 'Web', 'SMM', 'Campaign', 'Creatives', 'Coffee table Book'],
  COLORS: {
    ORANGE: '#FFE0B2',
    GREEN: '#C8E6C9',
    YELLOW: '#FFF9C4',
    RED: '#FFCDD2',
    HEADER_BG: '#1A237E',
    HEADER_FG: '#FFFFFF',
    SECTION_BG: '#E8EAF6',
    ALT_ROW: '#F5F5F5'
  }
};

// ===== MENU & TRIGGERS =====

function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Pipeline Tools')
    .addSubMenu(ui.createMenu('Filter & Sort')
      .addItem('Filter by Stage...', 'filterByStage')
      .addItem('Filter by Handled by...', 'filterByHandler')
      .addItem('Filter by Type of Scope...', 'filterByScope')
      .addSeparator()
      .addItem('Sort by Cost (High to Low)', 'sortByCostDesc')
      .addItem('Sort by Cost (Low to High)', 'sortByCostAsc')
      .addItem('Sort by Date (Newest First)', 'sortByDateDesc')
      .addItem('Sort by Date (Oldest First)', 'sortByDateAsc')
      .addItem('Sort by Stage (Pipeline Order)', 'sortByStageOrder')
      .addSeparator()
      .addItem('Clear All Filters', 'clearAllFilters'))
    .addSubMenu(ui.createMenu('Dashboard')
      .addItem('Generate / Refresh Dashboard', 'generateDashboard')
      .addItem('Go to Dashboard', 'goToDashboard'))
    .addSubMenu(ui.createMenu('Cleanup')
      .addItem('Find Duplicate Brands', 'findDuplicateBrands')
      .addItem('Standardize Phone Numbers', 'standardizePhones')
      .addItem('Clean Cost Values', 'cleanCostValues')
      .addItem('Highlight Incomplete Rows', 'highlightIncompleteRows')
      .addSeparator()
      .addItem('Run All Cleanup', 'runAllCleanup'))
    .addSubMenu(ui.createMenu('Stage Sheets')
      .addItem('Generate All Stage Sheets', 'generateAllStageSheets')
      .addItem('Refresh Closed Deals', 'refreshClosedDeals')
      .addItem('Refresh Active Pipeline', 'refreshActivePipeline')
      .addItem('Refresh Lost Deals', 'refreshLostDeals'))
    .addToUi();
}

// ===== UTILITY HELPERS =====

function getMainSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(CONFIG.MAIN_SHEET);
  if (!sheet) {
    throw new Error('Sheet "' + CONFIG.MAIN_SHEET + '" not found. Please rename your data sheet to "' + CONFIG.MAIN_SHEET + '".');
  }
  return sheet;
}

function getDataRows_(sheet) {
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return [];
  var lastCol = sheet.getLastColumn();
  return sheet.getRange(2, 1, lastRow - 1, lastCol).getValues();
}

function getHeaderRow_(sheet) {
  return sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
}

function parseCost(val) {
  if (val === null || val === undefined || val === '') return NaN;
  if (typeof val === 'number') return val;
  var str = String(val).trim();
  if (str === '-' || str === '' || /^tbd$/i.test(str) || /cost to be decided/i.test(str)) return NaN;

  // Handle multi-line values like "Website: 5,50,000\nBrand: TBD"
  if (str.indexOf('\n') !== -1) {
    var lines = str.split('\n');
    var total = 0;
    var found = false;
    for (var i = 0; i < lines.length; i++) {
      var lineNum = extractNumber_(lines[i]);
      if (!isNaN(lineNum)) {
        total += lineNum;
        found = true;
      }
    }
    return found ? total : NaN;
  }

  return extractNumber_(str);
}

function extractNumber_(str) {
  // Remove ₹ symbol, spaces, and "Rs" prefix
  var cleaned = str.replace(/[₹Rs.\s]/gi, '');
  // Remove commas (handles both Indian and international notation)
  cleaned = cleaned.replace(/,/g, '');
  // Extract the first number-like sequence
  var match = cleaned.match(/(\d+\.?\d*)/);
  if (match) return parseFloat(match[1]);
  return NaN;
}

function parseMessyDate(val) {
  if (val === null || val === undefined || val === '') return null;
  if (val instanceof Date && !isNaN(val.getTime())) return val;

  var str = String(val).trim();
  if (str === '' || str === '-') return null;

  // Strip ordinal suffixes: "14th" -> "14", "1st" -> "1", "2nd" -> "2", "3rd" -> "3"
  str = str.replace(/(\d+)(st|nd|rd|th)/gi, '$1');

  // Try direct parse first
  var d = new Date(str);
  if (!isNaN(d.getTime())) {
    // If year was not in the string, Date might default to 2001 or similar
    if (!/\d{4}/.test(String(val))) {
      var now = new Date();
      d.setFullYear(now.getFullYear());
      // If the date is more than 2 months in the future, assume previous year
      if (d.getTime() > now.getTime() + 60 * 24 * 60 * 60 * 1000) {
        d.setFullYear(now.getFullYear() - 1);
      }
    }
    return d;
  }

  // Try adding current year: "14 Jan" -> "14 Jan 2026"
  var now = new Date();
  d = new Date(str + ' ' + now.getFullYear());
  if (!isNaN(d.getTime())) {
    if (d.getTime() > now.getTime() + 60 * 24 * 60 * 60 * 1000) {
      d.setFullYear(now.getFullYear() - 1);
    }
    return d;
  }

  return null;
}

function formatINR(num) {
  if (isNaN(num) || num === null || num === undefined) return '-';
  var isNeg = num < 0;
  num = Math.abs(num);
  var parts = num.toFixed(2).split('.');
  var intPart = parts[0];
  var decPart = parts[1];

  // Indian grouping: last 3 digits, then groups of 2
  var result = '';
  if (intPart.length <= 3) {
    result = intPart;
  } else {
    result = intPart.slice(-3);
    var remaining = intPart.slice(0, -3);
    while (remaining.length > 2) {
      result = remaining.slice(-2) + ',' + result;
      remaining = remaining.slice(0, -2);
    }
    if (remaining.length > 0) {
      result = remaining + ',' + result;
    }
  }
  return (isNeg ? '-' : '') + '₹' + result + '.' + decPart;
}

function toast_(msg, title, seconds) {
  SpreadsheetApp.getActiveSpreadsheet().toast(msg, title || 'Pipeline Tools', seconds || 5);
}

function getOrCreateSheet_(name) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(name);
  if (sheet) {
    sheet.clear();
    // Remove any existing protection
    var protections = sheet.getProtections(SpreadsheetApp.ProtectionType.SHEET);
    for (var i = 0; i < protections.length; i++) {
      protections[i].remove();
    }
  } else {
    sheet = ss.insertSheet(name);
  }
  return sheet;
}

// ===== FILTER & SORT =====

function filterByStage() {
  try {
    var ui = SpreadsheetApp.getUi();
    var options = CONFIG.STAGES.join('\n');
    var result = ui.prompt('Filter by Stage',
      'Enter one of the following stages:\n\n' + options + '\n\n(Case-insensitive, partial match supported)',
      ui.ButtonSet.OK_CANCEL);
    if (result.getSelectedButton() !== ui.Button.OK) return;

    var query = result.getResponseText().trim().toLowerCase();
    if (!query) return;

    var sheet = getMainSheet_();
    clearAllFilters();
    var data = getDataRows_(sheet);
    var hidden = 0;

    for (var i = 0; i < data.length; i++) {
      var stage = String(data[i][CONFIG.COL.STAGE - 1]).trim().toLowerCase();
      if (stage.indexOf(query) === -1) {
        sheet.hideRows(i + 2);
        hidden++;
      }
    }
    toast_('Showing ' + (data.length - hidden) + ' of ' + data.length + ' rows matching "' + query + '"');
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error: ' + e.message);
  }
}

function filterByHandler() {
  try {
    var ui = SpreadsheetApp.getUi();
    var result = ui.prompt('Filter by Handler',
      'Enter handler name:\n\n' + CONFIG.HANDLERS.join(', ') + '\n\n(Case-insensitive)',
      ui.ButtonSet.OK_CANCEL);
    if (result.getSelectedButton() !== ui.Button.OK) return;

    var query = result.getResponseText().trim().toLowerCase();
    if (!query) return;

    var sheet = getMainSheet_();
    clearAllFilters();
    var data = getDataRows_(sheet);
    var hidden = 0;

    for (var i = 0; i < data.length; i++) {
      var handler = String(data[i][CONFIG.COL.HANDLER - 1]).trim().toLowerCase();
      if (handler.indexOf(query) === -1) {
        sheet.hideRows(i + 2);
        hidden++;
      }
    }
    toast_('Showing ' + (data.length - hidden) + ' of ' + data.length + ' rows for "' + query + '"');
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error: ' + e.message);
  }
}

function filterByScope() {
  try {
    var ui = SpreadsheetApp.getUi();
    var result = ui.prompt('Filter by Scope Type',
      'Enter scope type:\n\n' + CONFIG.SCOPES.join(', ') + '\n\n(Partial match — e.g., "Web" matches "Branding, Web")',
      ui.ButtonSet.OK_CANCEL);
    if (result.getSelectedButton() !== ui.Button.OK) return;

    var query = result.getResponseText().trim().toLowerCase();
    if (!query) return;

    var sheet = getMainSheet_();
    clearAllFilters();
    var data = getDataRows_(sheet);
    var hidden = 0;

    for (var i = 0; i < data.length; i++) {
      var scope = String(data[i][CONFIG.COL.SCOPE - 1]).trim().toLowerCase();
      if (scope.indexOf(query) === -1) {
        sheet.hideRows(i + 2);
        hidden++;
      }
    }
    toast_('Showing ' + (data.length - hidden) + ' of ' + data.length + ' rows for scope "' + query + '"');
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error: ' + e.message);
  }
}

function clearAllFilters() {
  try {
    var sheet = getMainSheet_();
    var lastRow = sheet.getLastRow();
    if (lastRow > 1) {
      sheet.showRows(2, lastRow - 1);
    }
    toast_('All filters cleared');
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error: ' + e.message);
  }
}

function sortByCostDesc() { sortByColumn_('cost', false); }
function sortByCostAsc() { sortByColumn_('cost', true); }
function sortByDateDesc() { sortByColumn_('date', false); }
function sortByDateAsc() { sortByColumn_('date', true); }

function sortByStageOrder() {
  try {
    var sheet = getMainSheet_();
    var data = getDataRows_(sheet);
    if (data.length === 0) return;

    var stageOrder = {};
    for (var i = 0; i < CONFIG.STAGES.length; i++) {
      stageOrder[CONFIG.STAGES[i].toLowerCase()] = i;
    }

    var indexed = data.map(function(row, idx) {
      var stage = String(row[CONFIG.COL.STAGE - 1]).trim().toLowerCase();
      var order = (stage in stageOrder) ? stageOrder[stage] : 999;
      return { row: row, order: order };
    });

    indexed.sort(function(a, b) { return a.order - b.order; });

    var sorted = indexed.map(function(item) { return item.row; });
    sheet.getRange(2, 1, sorted.length, sorted[0].length).setValues(sorted);
    toast_('Sorted by pipeline stage order');
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error: ' + e.message);
  }
}

function sortByColumn_(type, ascending) {
  try {
    var sheet = getMainSheet_();
    var data = getDataRows_(sheet);
    if (data.length === 0) return;

    var indexed = data.map(function(row) {
      var val;
      if (type === 'cost') {
        val = parseCost(row[CONFIG.COL.COSTS - 1]);
      } else {
        val = parseMessyDate(row[CONFIG.COL.DATE - 1]);
        val = val ? val.getTime() : NaN;
      }
      return { row: row, val: val };
    });

    indexed.sort(function(a, b) {
      var aValid = !isNaN(a.val);
      var bValid = !isNaN(b.val);
      if (!aValid && !bValid) return 0;
      if (!aValid) return 1;  // NaN goes to bottom
      if (!bValid) return -1;
      return ascending ? (a.val - b.val) : (b.val - a.val);
    });

    var sorted = indexed.map(function(item) { return item.row; });
    sheet.getRange(2, 1, sorted.length, sorted[0].length).setValues(sorted);
    var label = type === 'cost' ? 'cost' : 'date';
    var dir = ascending ? '(low to high)' : '(high to low)';
    toast_('Sorted by ' + label + ' ' + dir);
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error: ' + e.message);
  }
}

// ===== DEDUPLICATION & CLEANUP =====

function findDuplicateBrands() {
  try {
    var sheet = getMainSheet_();
    var data = getDataRows_(sheet);
    var brandMap = {};

    for (var i = 0; i < data.length; i++) {
      var brand = String(data[i][CONFIG.COL.BRAND - 1]).trim();
      if (!brand) continue;
      var key = brand.toLowerCase();
      if (!brandMap[key]) brandMap[key] = [];
      brandMap[key].push({ row: i + 2, name: brand });
    }

    var duplicates = [];
    var dupRows = [];
    for (var key in brandMap) {
      if (brandMap[key].length > 1) {
        duplicates.push(brandMap[key][0].name + ' (rows: ' +
          brandMap[key].map(function(d) { return d.row; }).join(', ') + ')');
        brandMap[key].forEach(function(d) { dupRows.push(d.row); });
      }
    }

    // Highlight duplicates
    for (var i = 0; i < dupRows.length; i++) {
      sheet.getRange(dupRows[i], CONFIG.COL.BRAND).setBackground(CONFIG.COLORS.ORANGE);
    }

    if (duplicates.length === 0) {
      SpreadsheetApp.getUi().alert('No duplicate brands found.');
    } else {
      SpreadsheetApp.getUi().alert('Found ' + duplicates.length + ' duplicate brand(s):\n\n' + duplicates.join('\n'));
    }
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error: ' + e.message);
  }
}

function standardizePhones() {
  try {
    var sheet = getMainSheet_();
    var data = getDataRows_(sheet);
    var changed = 0;

    for (var i = 0; i < data.length; i++) {
      var phone = String(data[i][CONFIG.COL.PHONE - 1]).trim();
      if (!phone || phone === '-' || phone.toLowerCase() === 'not available') continue;

      var original = phone;
      // Strip all non-digit characters except leading +
      var digits = phone.replace(/[^\d]/g, '');

      if (digits.length === 0) continue;

      var formatted = '';

      // Handle Indian mobile numbers
      if (digits.length === 10 && /^[6-9]/.test(digits)) {
        formatted = '+91 ' + digits.slice(0, 5) + ' ' + digits.slice(5);
      } else if (digits.length === 11 && digits.charAt(0) === '0') {
        // Leading 0 — remove and prepend +91
        digits = digits.slice(1);
        formatted = '+91 ' + digits.slice(0, 5) + ' ' + digits.slice(5);
      } else if (digits.length === 12 && digits.slice(0, 2) === '91') {
        formatted = '+91 ' + digits.slice(2, 7) + ' ' + digits.slice(7);
      } else if (digits.length === 13 && digits.slice(0, 3) === '919') {
        // +919XXXXXXXXX format (sometimes)
        formatted = '+91 ' + digits.slice(2, 7) + ' ' + digits.slice(7);
      } else {
        // International or unusual — just keep with spaces
        formatted = '+' + digits;
      }

      if (formatted && formatted !== original) {
        var row = i + 2;
        sheet.getRange(row, CONFIG.COL.PHONE).setValue(formatted);
        sheet.getRange(row, CONFIG.COL.PHONE).setBackground(CONFIG.COLORS.GREEN);
        changed++;
      }
    }
    toast_('Standardized ' + changed + ' phone number(s)');
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error: ' + e.message);
  }
}

function cleanCostValues() {
  try {
    var sheet = getMainSheet_();
    var data = getDataRows_(sheet);
    var cleaned = 0;
    var flagged = 0;

    for (var i = 0; i < data.length; i++) {
      var val = data[i][CONFIG.COL.COSTS - 1];
      var row = i + 2;
      var cell = sheet.getRange(row, CONFIG.COL.COSTS);

      if (val === null || val === undefined || val === '') continue;
      if (typeof val === 'number') continue; // Already clean

      var str = String(val).trim();

      // Flag TBD / non-numeric
      if (/^(tbd|cost to be decided|-|)$/i.test(str)) {
        cell.setBackground(CONFIG.COLORS.YELLOW);
        flagged++;
        continue;
      }

      // Multi-line values
      if (str.indexOf('\n') !== -1) {
        var total = parseCost(str);
        if (!isNaN(total)) {
          cell.setNote('Original: ' + str);
          cell.setValue(total);
          cell.setNumberFormat('₹#,##,##0.00');
          cell.setBackground(CONFIG.COLORS.GREEN);
          cleaned++;
        } else {
          cell.setBackground(CONFIG.COLORS.YELLOW);
          flagged++;
        }
        continue;
      }

      // Single ₹ value
      var num = parseCost(str);
      if (!isNaN(num)) {
        cell.setValue(num);
        cell.setNumberFormat('₹#,##,##0.00');
        if (String(val) !== String(num)) {
          cell.setBackground(CONFIG.COLORS.GREEN);
          cleaned++;
        }
      } else {
        cell.setBackground(CONFIG.COLORS.YELLOW);
        flagged++;
      }
    }
    toast_('Cleaned ' + cleaned + ' cost value(s), flagged ' + flagged + ' as TBD/unclear');
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error: ' + e.message);
  }
}

function highlightIncompleteRows() {
  try {
    var sheet = getMainSheet_();
    var data = getDataRows_(sheet);
    var incomplete = 0;

    var requiredCols = [CONFIG.COL.BRAND, CONFIG.COL.PHONE, CONFIG.COL.EMAIL, CONFIG.COL.STAGE];

    for (var i = 0; i < data.length; i++) {
      var row = i + 2;
      var rowIncomplete = false;
      for (var j = 0; j < requiredCols.length; j++) {
        var val = String(data[i][requiredCols[j] - 1]).trim();
        if (!val || val === '-' || val.toLowerCase() === 'not available' || val.toLowerCase() === 'na') {
          sheet.getRange(row, requiredCols[j]).setBackground(CONFIG.COLORS.RED);
          rowIncomplete = true;
        }
      }
      if (rowIncomplete) incomplete++;
    }
    toast_('Found ' + incomplete + ' row(s) with missing data (highlighted in red)');
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error: ' + e.message);
  }
}

function runAllCleanup() {
  try {
    toast_('Running all cleanup tasks...', 'Cleanup', 10);
    findDuplicateBrands();
    standardizePhones();
    cleanCostValues();
    highlightIncompleteRows();
    toast_('All cleanup tasks completed!');
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error during cleanup: ' + e.message);
  }
}

// ===== CROSS-SHEET OPERATIONS =====

function generateAllStageSheets() {
  try {
    toast_('Generating stage sheets...', 'Stage Sheets', 10);
    refreshClosedDeals();
    refreshActivePipeline();
    refreshLostDeals();
    toast_('All stage sheets generated!');
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error: ' + e.message);
  }
}

function refreshClosedDeals() {
  generateStageSheet_(CONFIG.CLOSED_SHEET, function(row) {
    return String(row[CONFIG.COL.STAGE - 1]).trim() === 'Closed';
  }, '#4CAF50');
}

function refreshActivePipeline() {
  generateStageSheet_(CONFIG.ACTIVE_SHEET, function(row) {
    var stage = String(row[CONFIG.COL.STAGE - 1]).trim();
    return CONFIG.ACTIVE_STAGES.indexOf(stage) !== -1;
  }, '#2196F3');
}

function refreshLostDeals() {
  generateStageSheet_(CONFIG.LOST_SHEET, function(row) {
    return String(row[CONFIG.COL.STAGE - 1]).trim() === 'Didnt work out';
  }, '#F44336');
}

function generateStageSheet_(sheetName, filterFn, tabColor) {
  try {
    var mainSheet = getMainSheet_();
    var headers = getHeaderRow_(mainSheet);
    var data = getDataRows_(mainSheet);

    var filtered = data.filter(filterFn);

    var sheet = getOrCreateSheet_(sheetName);

    // Write headers
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.getRange(1, 1, 1, headers.length)
      .setBackground(CONFIG.COLORS.HEADER_BG)
      .setFontColor(CONFIG.COLORS.HEADER_FG)
      .setFontWeight('bold');
    sheet.setFrozenRows(1);

    // Write data
    if (filtered.length > 0) {
      sheet.getRange(2, 1, filtered.length, filtered[0].length).setValues(filtered);

      // Alternating row colors
      for (var i = 0; i < filtered.length; i++) {
        if (i % 2 === 1) {
          sheet.getRange(i + 2, 1, 1, headers.length).setBackground(CONFIG.COLORS.ALT_ROW);
        }
      }
    }

    // Format cost column
    if (filtered.length > 0) {
      sheet.getRange(2, CONFIG.COL.COSTS, filtered.length, 1).setNumberFormat('₹#,##,##0.00');
    }

    // Auto-resize
    for (var c = 1; c <= headers.length; c++) {
      sheet.autoResizeColumn(c);
    }

    // Tab color
    sheet.setTabColor(tabColor);

    // Protection warning
    var protection = sheet.protect().setDescription('Auto-generated sheet');
    protection.setWarningOnly(true);

    // Note on A1
    sheet.getRange(1, 1).setNote('Auto-generated from ' + CONFIG.MAIN_SHEET + ' sheet.\nUse Pipeline Tools > Stage Sheets > Refresh to update.\nLast updated: ' + new Date().toLocaleString());

    toast_(sheetName + ': ' + filtered.length + ' rows');
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error generating ' + sheetName + ': ' + e.message);
  }
}

// ===== DASHBOARD =====

function generateDashboard() {
  try {
    toast_('Generating dashboard...', 'Dashboard', 15);

    var mainSheet = getMainSheet_();
    var data = getDataRows_(mainSheet);
    var sheet = getOrCreateSheet_(CONFIG.DASHBOARD_SHEET);

    // ── Aggregate data ──
    var stageCounts = {};
    var stageTotals = {};
    var handlerStats = {};
    var scopeStats = {};
    var tbdCount = 0;

    CONFIG.STAGES.forEach(function(s) { stageCounts[s] = 0; stageTotals[s] = 0; });
    CONFIG.HANDLERS.forEach(function(h) {
      handlerStats[h] = { total: 0, closed: 0, revenue: 0 };
    });

    for (var i = 0; i < data.length; i++) {
      var row = data[i];
      var stage = String(row[CONFIG.COL.STAGE - 1]).trim();
      var handler = String(row[CONFIG.COL.HANDLER - 1]).trim();
      var cost = parseCost(row[CONFIG.COL.COSTS - 1]);
      var scope = String(row[CONFIG.COL.SCOPE - 1]).trim();

      // Stage aggregation
      if (stage in stageCounts) {
        stageCounts[stage]++;
        if (!isNaN(cost)) stageTotals[stage] += cost;
      }

      // Handler aggregation
      if (handler in handlerStats) {
        handlerStats[handler].total++;
        if (stage === 'Closed') {
          handlerStats[handler].closed++;
          if (!isNaN(cost)) handlerStats[handler].revenue += cost;
        }
      }

      // Scope aggregation
      var scopes = scope.split(',').map(function(s) { return s.trim(); });
      scopes.forEach(function(s) {
        if (!s) return;
        if (!scopeStats[s]) scopeStats[s] = { count: 0, value: 0 };
        scopeStats[s].count++;
        if (!isNaN(cost)) scopeStats[s].value += cost;
      });

      // TBD count
      var costStr = String(row[CONFIG.COL.COSTS - 1]).trim().toLowerCase();
      if (costStr === 'tbd' || costStr === 'cost to be decided') tbdCount++;
    }

    // ── Write Dashboard ──
    var r = 1;

    // Title
    sheet.getRange(r, 1, 1, 6).merge();
    sheet.getRange(r, 1).setValue('PIPELINE DASHBOARD')
      .setFontSize(18).setFontWeight('bold')
      .setBackground(CONFIG.COLORS.HEADER_BG).setFontColor(CONFIG.COLORS.HEADER_FG)
      .setHorizontalAlignment('center');
    r++;
    sheet.getRange(r, 1).setValue('Last Updated: ' + new Date().toLocaleString())
      .setFontStyle('italic').setFontColor('#666666');
    r += 2;

    // ── Section: Pipeline Summary by Stage ──
    sheet.getRange(r, 1, 1, 4).merge();
    sheet.getRange(r, 1).setValue('PIPELINE SUMMARY BY STAGE')
      .setFontSize(13).setFontWeight('bold').setBackground(CONFIG.COLORS.SECTION_BG);
    r++;

    // Headers
    var stageHeaders = ['Stage', 'Count', 'Total Value', 'Avg Deal Size'];
    sheet.getRange(r, 1, 1, 4).setValues([stageHeaders])
      .setFontWeight('bold').setBackground('#CFD8DC');
    r++;

    var grandTotal = 0;
    var grandCount = 0;

    CONFIG.STAGES.forEach(function(stage) {
      var count = stageCounts[stage];
      var total = stageTotals[stage];
      var avg = count > 0 ? total / count : 0;
      sheet.getRange(r, 1).setValue(stage);
      sheet.getRange(r, 2).setValue(count);
      sheet.getRange(r, 3).setValue(total).setNumberFormat('₹#,##,##0.00');
      sheet.getRange(r, 4).setValue(avg).setNumberFormat('₹#,##,##0.00');
      grandTotal += total;
      grandCount += count;
      r++;
    });

    // Grand total row
    sheet.getRange(r, 1).setValue('TOTAL').setFontWeight('bold');
    sheet.getRange(r, 2).setValue(grandCount).setFontWeight('bold');
    sheet.getRange(r, 3).setValue(grandTotal).setNumberFormat('₹#,##,##0.00').setFontWeight('bold');
    sheet.getRange(r, 4).setValue(grandCount > 0 ? grandTotal / grandCount : 0)
      .setNumberFormat('₹#,##,##0.00').setFontWeight('bold');
    r += 2;

    // ── Section: Revenue Metrics ──
    sheet.getRange(r, 1, 1, 2).merge();
    sheet.getRange(r, 1).setValue('REVENUE METRICS')
      .setFontSize(13).setFontWeight('bold').setBackground(CONFIG.COLORS.SECTION_BG);
    r++;

    var closedRevenue = stageTotals['Closed'] || 0;
    var activePipelineValue = (stageTotals['First Call'] || 0) + (stageTotals['Pitch'] || 0) + (stageTotals['Commercials'] || 0);
    var totalPipelineValue = closedRevenue + activePipelineValue;

    var metrics = [
      ['Closed Revenue', closedRevenue],
      ['Active Pipeline Value', activePipelineValue],
      ['Total Pipeline Value (excl. Lost)', totalPipelineValue],
      ['Average Deal Size (all stages)', grandCount > 0 ? grandTotal / grandCount : 0],
      ['Deals with TBD Costs', tbdCount]
    ];

    metrics.forEach(function(m) {
      sheet.getRange(r, 1).setValue(m[0]).setFontWeight('bold');
      if (typeof m[1] === 'number' && m[0] !== 'Deals with TBD Costs') {
        sheet.getRange(r, 2).setValue(m[1]).setNumberFormat('₹#,##,##0.00');
      } else {
        sheet.getRange(r, 2).setValue(m[1]);
      }
      r++;
    });
    r++;

    // ── Section: Team Performance ──
    sheet.getRange(r, 1, 1, 5).merge();
    sheet.getRange(r, 1).setValue('TEAM PERFORMANCE')
      .setFontSize(13).setFontWeight('bold').setBackground(CONFIG.COLORS.SECTION_BG);
    r++;

    var teamHeaders = ['Team Member', 'Total Deals', 'Closed', 'Closing Rate', 'Revenue'];
    sheet.getRange(r, 1, 1, 5).setValues([teamHeaders])
      .setFontWeight('bold').setBackground('#CFD8DC');
    r++;

    CONFIG.HANDLERS.forEach(function(handler) {
      var stats = handlerStats[handler];
      var rate = stats.total > 0 ? (stats.closed / stats.total * 100).toFixed(1) + '%' : '0%';
      sheet.getRange(r, 1).setValue(handler);
      sheet.getRange(r, 2).setValue(stats.total);
      sheet.getRange(r, 3).setValue(stats.closed);
      sheet.getRange(r, 4).setValue(rate);
      sheet.getRange(r, 5).setValue(stats.revenue).setNumberFormat('₹#,##,##0.00');
      r++;
    });
    r++;

    // ── Section: Scope Type Breakdown ──
    sheet.getRange(r, 1, 1, 3).merge();
    sheet.getRange(r, 1).setValue('SCOPE TYPE BREAKDOWN')
      .setFontSize(13).setFontWeight('bold').setBackground(CONFIG.COLORS.SECTION_BG);
    r++;

    var scopeHeaders = ['Scope Type', 'Count', 'Value'];
    sheet.getRange(r, 1, 1, 3).setValues([scopeHeaders])
      .setFontWeight('bold').setBackground('#CFD8DC');
    r++;

    var scopeKeys = Object.keys(scopeStats).sort(function(a, b) {
      return scopeStats[b].count - scopeStats[a].count;
    });

    scopeKeys.forEach(function(key) {
      sheet.getRange(r, 1).setValue(key);
      sheet.getRange(r, 2).setValue(scopeStats[key].count);
      sheet.getRange(r, 3).setValue(scopeStats[key].value).setNumberFormat('₹#,##,##0.00');
      r++;
    });

    // Auto-resize
    for (var c = 1; c <= 6; c++) {
      sheet.autoResizeColumn(c);
    }

    sheet.setTabColor('#FF9800');
    toast_('Dashboard generated with ' + data.length + ' records!');
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error generating dashboard: ' + e.message);
  }
}

function goToDashboard() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.DASHBOARD_SHEET);
    if (!sheet) {
      SpreadsheetApp.getUi().alert('Dashboard not found. Use Pipeline Tools > Dashboard > Generate first.');
      return;
    }
    sheet.activate();
  } catch (e) {
    SpreadsheetApp.getUi().alert('Error: ' + e.message);
  }
}
