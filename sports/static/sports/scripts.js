document.addEventListener('DOMContentLoaded', function() {
    
    console.log("DOM loaded");
    document.querySelector('#all-events-view').style.display = 'block';
    document.querySelector('#event-view').style.display = 'none';
    document.querySelector('#notlogged').style.display = 'none';

    document.querySelector('#close').addEventListener("click", close);

    document.getElementById('past_btn').addEventListener("click", past);


    // By default, load all events function
    allevents();
    
});
function close(){
    document.querySelector('#event-view').style.display = 'none';
    
    // Refresh the page
    location.reload();
}

function past(){
    document.querySelector('#all-events-view').style.display = 'none';
    document.querySelector('#past-events-view').style.display = 'block';
    
    // Fetching past events
    fetch('past_events')
    .then(response => response.json())
    .then(data => {
        console.log("past data",data);
        const object = data;
        const contained = document.querySelector('#list3');
        object.forEach(function(element){

        let e = document.createElement('li');
        // Give div a border
        e.style.border = 'solid thin';
        e.style.borderRadius = "50px";

        // Add margin or padding to div
        e.style.marginBottom = "10px";
        e.style.marginTop = "11px";
        e.style.paddingTop = "5px";
        e.style.paddingLeft = "5px";
        e.style.paddingRight = "5px";

        // Hover
        e.addEventListener("mouseover", function(){
            e.style.transform = 'scale(1.05)';
          }),
          e.addEventListener("mouseout", function(){
            e.style.transform = 'scale(1)';  
          })
        // Create variable for attendees and comma and space
        var attendees = element.attendees;
        var spaced = attendees.join(', ');

        e.innerHTML += `<h4 list-style-type: none; style='text-decoration:underline;'>Title: ${element.title}  </h4>`;
        e.innerHTML += `<li>Description: ${element.description} </li>`; 
        e.innerHTML += `<li>Host: ${element.host} </li>`;
        e.innerHTML +=  `<li>Attendees: ${spaced} </li>`;
        e.innerHTML +=  `<li>Date: ${element.date} </li>`;
        e.innerHTML +=  `<li>Start: ${element.start} </li>`;
        e.innerHTML +=  `<li>End: ${element.end} </li>`;
        e.innerHTML +=  `<li>Category: ${element.category} </li>`;
        e.innerHTML +=  `<li>Number Attending: ${element.number_attending} </li>`;
        if (element.image){
            e.innerHTML +=  `<li>Location: ${element.location} </li><br>`;
            e.innerHTML +=  `<img src="/media/${element.image}" width="40%" height="40%"><br><br>`;
        }
        else {
            e.innerHTML +=  `<li>Location: ${element.location} </li><br><br>`;
        }
        contained.append(e);

        // Ability to click email
        e.addEventListener('click', function(){
            document.querySelector('#past-events-view').style.display = 'none';
            document.querySelector('#event-view').style.display = 'block';

            // Send id for display
            single_event(element.id, 'past');
        });
        })
    })
}

async function allevents() {
    //document.querySelector('#all-events-view').style.display = 'block';

    // Make a fetch request
    const response = await fetch('events');
    const data = await response.json();
    console.log("DATA",data)
    return data;
    }
    allevents().then(data => {
        const object = data;
        const contained = document.querySelector('#list1');
        object.forEach(function(element){
           
            
        let e = document.createElement('li');

        // Give div a border
        e.style.border = 'solid thin';
        e.style.borderRadius = "50px";

        // Add margin or padding to div
        e.style.marginBottom = "10px";
        e.style.marginTop = "11px";
        e.style.paddingTop = "5px";
        e.style.paddingLeft = "5px";
        e.style.paddingRight = "5px";
   
        

        // Hover
        e.addEventListener("mouseover", function(){
            e.style.transform = 'scale(1.05)';
          }),
          e.addEventListener("mouseout", function(){
            e.style.transform = 'scale(1)';  
          })
        // Create variable for attendees and comma and space
        var attendees = element.attendees;
        var spaced = attendees.join(', ');

        e.innerHTML += `<h4 list-style-type: none; style='text-decoration:underline;'>Title: ${element.title}  </h4>`;
        e.innerHTML += `<li>Description: ${element.description} </li>`; 
        e.innerHTML += `<li>Host: ${element.host} </li>`;
        e.innerHTML +=  `<li>Attendees: ${spaced} </li>`;
        e.innerHTML +=  `<li>Date: ${element.date} </li>`;
        e.innerHTML +=  `<li>Start: ${element.start} </li>`;
        e.innerHTML +=  `<li>End: ${element.end} </li>`;
        e.innerHTML +=  `<li>Category: ${element.category} </li>`;
        e.innerHTML +=  `<li>Number Attending: ${element.number_attending} </li>`;
        if (element.image){
            e.innerHTML +=  `<li>Location: ${element.location} </li><br>`;
            e.innerHTML +=  `<img src="/media/${element.image}" width="40%" height="40%"><br><br>`;
        }
        else {
            e.innerHTML +=  `<li>Location: ${element.location} </li><br><br>`;
        }
        contained.append(e);

        // Ability to click email
        e.addEventListener('click', function(){
            document.querySelector('#all-events-view').style.display = 'none';
            document.querySelector('#event-view').style.display = 'block';

            console.log("This ID clicked:", element.id);
            // Show event view
            // Send id for display
            single_event(element.id, 'upcoming'); 
        })
        })
    });
 

let autocomplete;
function initAutocomplete() {
    console.log("api is being called...");
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('autocomplete'),
        {
            types: ['establishment'],
            componentRestrictions: {'country': ['US']},
            fields: ['place_id', 'geometry', 'name', 'formatted_address']
        });
    autocomplete.addListener('place_changed', onPlaceChanged);
}


function onPlaceChanged() {
    var place = autocomplete.getPlace();
    console.log(place)


    if (!place.geometry) {
        // user did not select a prediction; reset the input field
        document.getElementById('autocomplete').value = '';
        alert("Invalid place");

    } else {
        // Display details about the valid place
        //document.getElementById('details').innerHTML = place.name;
        document.getElementById('autocomplete').value = place.formatted_address;
    }
}

function single_event(id, time){      
    document.querySelector('#list2').innerHTML = ''; 
       
    
    console.log("Single event ran", id)
    
    // Create int variable for route
    let variable = id;
  
    // Make a get request
    fetch(`event/${variable}`)
    .then(response => response.json())
    .then(data => {
    const object = data;
    const contained2 = document.querySelector('#list2');
    
    let e = document.createElement('li');

    // Give div a border
    e.style.border = 'solid thin';
    e.style.borderRadius = "50px";

    // Add margin or padding to div
    e.style.marginBottom = "10px";
    e.style.marginTop = "11px";
    e.style.paddingTop = "5px";
    e.style.paddingLeft = "5px";
    e.style.paddingRight = "5px";

    // Create variable for attendees and comma and space
    var attendees = object.attendees;
    var spaced = attendees.join(', ');
    

    e.innerHTML += `<h4 list-style-type: none; style='text-decoration:underline;'>Title: ${object.title}  </h4>`;
    e.innerHTML += `<li>Description: ${object.description} </li>`; 
    e.innerHTML += `<li>Host: ${object.host} </li>`;
    e.innerHTML +=  `<li>Attendees: ${spaced} </li>`;
    e.innerHTML +=  `<li>Date: ${object.date} </li>`;
    e.innerHTML +=  `<li>Start: ${object.start} </li>`;
    e.innerHTML +=  `<li>End: ${object.end} </li>`;
    e.innerHTML +=  `<li>Category: ${object.category} </li>`;
    e.innerHTML +=  `<li>Number Attending: ${object.number_attending} </li>`;
    if (object.image){
        e.innerHTML +=  `<li>Location: ${object.location} </li><br>`;
        e.innerHTML +=  `<img src="/media/${object.image}" width="40%" height="40%"><br><br>`;
    }
    else {
        e.innerHTML +=  `<li>Location: ${object.location} </li><br><br>`;
    }
    
    contained2.append(e);
    
    if (time === 'upcoming'){
    try {
        var username = document.getElementById('username').innerHTML;
        let button = document.createElement('button');
        // If host, give option to cancel event
        if (username === object.host){
            button.textContent = 'Cancel Event';   
        }
        // If new condition is true and first condition false
        else if (spaced.includes(username) && !(username === object.host)) {
            button.textContent = 'Unattend';
        }
        // If both conditions are false
        else {
            button.textContent = 'Attend';
        }

        contained2.append(button);
        // Listen for button click and send access type to function 
        button.addEventListener('click', () => {
            event_access(button.textContent, object.id, username);
        }); 

    }
    catch(err) {
        console.log("Error:", err);
        contained2.append(e);
        document.querySelector('#notlogged').style.display = 'block';
    }
    }// if statement
    if (time === 'past'){
    try{
        var username = document.getElementById('username').innerHTML;
        let button = document.createElement('button');
        if (username === object.host){
            button.textContent = 'Delete Past Event'; 
            contained2.append(button); 
        }
        // Listen for button click and send access type to function 
        button.addEventListener('click', () => {
            event_access(button.textContent, object.id, username);
        });
        
    }
    catch(err){
        console.log("Error:", err);
    }
    }
    });
}



// Receives access type to do something
async function event_access(access, id, username){
    if (access === "Attend" || access === "Unattend"){
        console.log("Testing", access, id, username);
       // Make a put request
    fetch(`update/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id:id,
            attendees:username,
            number_attending:1
        })
    })
    .then(location.reload())
    //.then(response => response.json())
    .then(data => {
        console.log("From update",data);
    })
    .catch(error => {
        console.log(error);
    }); 
    }
    
    // Cancel or Delete event
    if (access === 'Cancel Event'|| access === "Delete Past Event"){
        try{
            const response = await fetch(`delete/${id}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')}
              });
            
              if (!response.ok) {
                const message = 'Error with Status Code: ' + response.status;
                throw new Error(message);
              };
              const data = await response.json();
              console.log("data from cancel/delete:", data);
            } 
        catch (error) {
              console.log('Error:', error);
            }
            location.reload()    
    } 


}
// Use this to grab the csrf token
function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}