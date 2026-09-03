// Google Apps Script (GAS) API Endpoint for Magical Kingdom Sync

function doGet(e) {
  return handleRequest(e, 'GET');
}

function doPost(e) {
  return handleRequest(e, 'POST');
}

function handleRequest(e, method) {
  try {
    let payload = {};
    if (method === 'POST') {
      if (!e.postData || !e.postData.contents) {
        throw new Error("No post data received");
      }
      payload = JSON.parse(e.postData.contents);
    } else {
      payload = e.parameter;
    }

    const action = payload.action;
    
    switch (action) {
      case 'SYNC_PROGRESS':
        return syncProgress(payload);
      case 'LOG_TELEMETRY':
        return logTelemetry(payload);
      case 'GET_PROFILE':
        return getProfile(payload);
      default:
        return createResponse({ status: "error", message: "Unknown action" }, 400);
    }
  } catch (error) {
    return createResponse({ status: "error", message: error.toString() }, 500);
  }
}

function syncProgress(payload) {
  const profileId = payload.profileId;
  const incomingNodes = parseInt(payload.nodesCompleted) || 0;
  const incomingStars = parseInt(payload.stars) || 0;
  const timestamp = payload.timestamp || new Date().toISOString();
  
  if (!profileId) {
    return createResponse({ status: "error", message: "Missing profileId" }, 400);
  }
  
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("MapProgress");
  if (!sheet) {
    throw new Error("MapProgress sheet not found");
  }
  
  const data = sheet.getDataRange().getValues();
  let foundRowIndex = -1;
  let maxNodes = incomingNodes;
  let maxStars = incomingStars;

  // Search for existing profile (assuming row 1 is header, so start from 1)
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === profileId) {
      foundRowIndex = i + 1; // 1-indexed for SpreadsheetApp
      const existingNodes = parseInt(data[i][1]) || 0;
      const existingStars = parseInt(data[i][2]) || 0;
      
      // Conflict Resolution: Highest Wins
      maxNodes = Math.max(incomingNodes, existingNodes);
      maxStars = Math.max(incomingStars, existingStars);
      break;
    }
  }

  if (foundRowIndex > -1) {
    // Update existing row
    sheet.getRange(foundRowIndex, 2).setValue(maxNodes);
    sheet.getRange(foundRowIndex, 3).setValue(maxStars);
    sheet.getRange(foundRowIndex, 4).setValue(timestamp);
  } else {
    // Append new row
    sheet.appendRow([profileId, maxNodes, maxStars, timestamp]);
  }
  
  return createResponse({ 
    status: "success", 
    profileId: profileId, 
    syncedNodes: maxNodes,
    syncedStars: maxStars
  });
}

function logTelemetry(payload) {
  const uuid = payload.uuid;
  const eventData = JSON.stringify(payload.events || []);
  const timestamp = new Date().toISOString();
  
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("TelemetryLogs");
  if (!sheet) {
    throw new Error("TelemetryLogs sheet not found");
  }
  
  sheet.appendRow([uuid, eventData, timestamp]);
  
  return createResponse({ status: "success" });
}

function getProfile(payload) {
  // Stub for fetching profile data across devices using 4-digit PIN
  return createResponse({ status: "success", message: "Not implemented yet" });
}

function createResponse(data, statusCode = 200) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
