import React, {useEffect, useState} from 'react';
import GuessButton from './GuessButton';
import axios from 'axios';

let categories = ["accessory", "cats", "construction", "fruit", "instrument", "one_liner", "plant", "shape", 
    "sport", "terrain", "tool", "vehicle", "weapon", "weather", "writing_utencil"];

let correct = {}
const DrawingBoard = () => {
    

    const [guesses, setGuesses] = useState([]);

    useEffect(() => {
      const localCategories = localStorage.getItem('categories');
      if (localCategories) {
        categories = JSON.parse(localCategories);
      }
      const localCorrect = localStorage.getItem('correct');
      if (localCorrect) {
         correct = JSON.parse(localCorrect);
      }
    }, []);

    const resetLocalStorage = () => {
        console.log('resetting local storage')
        localStorage.setItem('categories', JSON.stringify(["accessory", "cats", "construction", "fruit", "instrument", "one_liner", "plant", "shape", 
        "sport", "terrain", "tool", "vehicle", "weapon", "weather", "writing_utencil"]));
        localStorage.setItem('correct', JSON.stringify({}));
    }


    setInterval(() => {
        async function getData() {
            console.log('getting data')
            try {
                const response = await axios.get('http://localhost:5555/scored');
                const data = await response.data;
    
                if (data.scored) {
                    localStorage.setItem('categories', JSON.stringify([
                        "accessory", "cats", "construction", "fruit", 
                        "instrument", "one_liner", "plant", "shape", 
                        "sport", "terrain", "tool", "vehicle",
                        "weapon", "weather", "writing_utencil"
                    ]));
                    
                    let correct = JSON.parse(localStorage.getItem('correct')) || {}
    
                    if (correct[data.correct]) {
                        correct[data.correct] += 1;
                    } else {
                        correct[data.correct] = 1;
                    }
                    
                    localStorage.setItem('correct', JSON.stringify(correct));
                    const response2 = await axios.get('http://localhost:5555/disableScored');
                    const data2 = await response2.data;
                }
    
            } catch(error) {
                console.error("Error fetching data: ", error);
            }
        }
        getData();
    }, 1000);

  const handleGuess = (category) => {
    async function postData() {
      const response = await axios.post('http://localhost:5555/finalGuess', {
        guess: category
      });
      const data = await response.data;
      console.log(data);
      const updatedGuesses = [...guesses, category];
      setGuesses(updatedGuesses);


      categories.splice(categories.indexOf(category), 1);

      localStorage.setItem('categories', JSON.stringify(categories));
    }
    postData();
  };

  const [path, setPath] = useState('');
  
//   setInterval(() => {
//     try {
//         const path = require('../img.png');
//         setPath(path);
//     } catch (e) {
//         const path = require('../logo.svg');
//         setPath(path);
//         }
//     }, 1000);

    const getColor = (category) => {
        const localCorrectCounts = JSON.parse(localStorage.getItem('correct'));
        const count = localCorrectCounts[category] || 0;
    
        // Return color based on count
        if (count < 1) return 'lightgreen';
        if (count < 3) return 'green';
        return 'darkgreen';
      };
    


  return (
    <div>
      <div>
        <img className="scribble" src={require('../img.png')} />
      </div>
      {categories.map(category => 
        <GuessButton key={category} category={category} onGuess={handleGuess} color={getColor(category)}/>
      )}
      

      <div>
        <button onClick={resetLocalStorage}>Reset</button>
      </div>
    </div>
  );
};

export default DrawingBoard;