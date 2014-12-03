var fileMapping = {};
var cursorMapping = {};
var tabMapping = {};
var bufferMapping = {};
var currentTab = undefined;

function CharacterBuffer(fileId, cursor, data) {
    this.fileId = fileId;
    this.contents = data || '';
    this.cursor = cursor;

    this.writeContent = function(data) {
        var pos = this.cursor.position;
        var temp = this.contents.substring(0, pos);
        var temp2 = this.contents.substring(pos, this.contents.length);
        this.contents = temp + data + temp2;
        this.cursor.position += data.length;
    };

    this.deleteContent = function(length) {
        var pos = this.cursor.position;
        var temp = this.contents.substring(0, pos);
        var temp2 = this.contents.substring(pos+length, this.contents.length);
        this.contents = temp + temp2;
    };

    this.moveCursor = function(move) {
        this.cursor.position += move;
    };
    
    this.moveCursorTo = function(pos) {
        this.cursor.position = pos;
    };
}

function EditorTab(fileId) {
    this.fileId = fileId;
    this.file = fileMapping[fileId];
    this.text = this.file.name;

    // create new GUI tab
    var tabs = $('#tabs>.editorTabs');
    var newTab = $('<li tabId="'+fileId+'"><a href="#content-' + fileId + '">' + this.file.name + '</a></li>');
    tabs.append(newTab);

    // create tab content
    var fileContent = bufferMapping[fileId].contents;
    var tabContent = $('<div id="content-' + fileId + '"></div');
    tabContent.append('<textarea>' + fileContent + '</textarea>');
    $('#tabs').append(tabContent);
    $('#tabs').tabs('refresh');

    return newTab;
}

function EditorFile(name) {
    this.name = name;
    this.fileId = getNewFileId();
}

function Cursor(fileId) {
    this.fileId = fileId;
    this.position = 0;
}

function getNewFileId() {
    var numFiles = Object.keys(fileMapping).length;
    return ++numFiles;
}

function saveFile() {
    if (currentTab == undefined) {
        console.log("No file specified to save");
    }

    var file = fileMapping[currentTab];
}

function openFile() {
    var file = undefined;
    var name = '';
    var reader = new FileReader();
    reader.onload = function(event) {
        var text = reader.result;
        finish(file, name, text);
    };
    var fileDialog = $('<input type="file"/>');
    fileDialog.on('change', function(e) {
        file = this.files[0];
        name = file.name;
        reader.readAsText(file);
    });
    fileDialog.click();


    this.chooseFile = function(event) {
        file = fileDialog.files[0];
        name = file.name;
        reader.readAsText(file);
    };

    var finish = function(thisFile, fileName, contents) {
        var fileId = getNewFileId();
        var cursor = new Cursor(fileId);
        cursorMapping[fileId] = cursor;
        var buffer = new CharacterBuffer(fileId, cursor, contents);
        bufferMapping[fileId] = buffer;
        fileMapping[fileId] = {
            file: file,
            name: fileName,
            contents: buffer
        };

        // create new tab
        var tab = new EditorTab(fileId);
        tabMapping[fileId] = tab;
    };

}

function handleFileOpen() {

}

function runApp() {
    var editorTabs = $('#tabs');
    editorTabs.tabs({
        activate: function(event, ui) {
            // set current tab
            currentTab = ui.newTab.attr('tabid');
        }
    });
    editorTabs.find('.ui-tabs-nav').sortable({
        axis: 'x',
        stop: function() {
            editorTabs.tabs('refresh');
        }    
    });
}
