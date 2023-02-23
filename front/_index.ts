// Import the express in typescript file
import express from 'express';
 
// Initialize the express engine
const app: express.Application = express();
 
 
// app.use('/flash/', flashRouter);
// app.use('/sofa/', sofaRouter);

// Handling '/' Request
app.get('/', (_req, _res) => {
    _res.send("TypeScript With Express fer");
});
 
// Server setup
app.listen(3000, () => {
    console.log(`TypeScript with Express 
        http://localhost:3000/`);
});