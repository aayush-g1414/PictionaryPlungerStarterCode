import React from 'react';

const GuessButton = ({category, onGuess, color}) => (
  <button style={{backgroundColor: color}} onClick={() => onGuess(category)}>
    {category}
  </button>
);

export default GuessButton;