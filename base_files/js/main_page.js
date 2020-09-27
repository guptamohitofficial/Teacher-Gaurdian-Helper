var tabButtons=document.querySelectorAll(".tabContainer .buttonContainer button");
var tabPanels=document.querySelectorAll(".tabContainer  .tabPanel");

function showPanel(panelIndex,colorCode) {
    tabButtons.forEach(function(node){
        node.style.backgroundColor="";
        node.style.color="";
    });
    tabButtons[panelIndex].style.backgroundColor=colorCode;
    tabButtons[panelIndex].style.color="#03a9f4";
    tabPanels.forEach(function(node){
        node.style.display="none";
    });
    tabPanels[panelIndex].style.display="block";
    tabPanels[panelIndex].style.backgroundColor='#fff';
}




var tabButtons1=document.querySelectorAll(".tabContainer1 .buttonContainer1 button");
var tabPanels1=document.querySelectorAll(".tabContainer1  .tabPanel1");

function showPanel1(panelIndex1,colorCode1) {
    tabButtons1.forEach(function(node1){
        node1.style.backgroundColor="";
        node1.style.color="";
    });
    tabButtons1[panelIndex1].style.backgroundColor=colorCode1;
    tabButtons1[panelIndex1].style.color="#03a9f4";
    tabPanels1.forEach(function(node1){
        node1.style.display="none";
    });
    tabPanels1[panelIndex1].style.display="block";
    tabPanels1[panelIndex1].style.backgroundColor=colorCode1;
}
