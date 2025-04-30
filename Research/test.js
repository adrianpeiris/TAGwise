const vidurl = 'https://www.youtube.com/watch?v=--5E3f1H-U0';

fetch(`https://noembed.com/embed?dataType=json&url=${vidurl}`)
  .then(res => res.json())
  .then(data => {
    console.log('Title:', data);
    console.log('Title:', data.title);
    console.log('Description:', data.description); // Assuming description is available
  })
  .catch(error => console.error('Error:', error));