import dotenv from "dotenv";
import express from "express";
import chalk from "chalk";
import cors from "cors";

dotenv.config();

const app = express();
const port = process.env.PORT;
app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.send("Hello, Express!");
});

app.listen(port, () => {
  console.log(chalk.bgGreen(`Server is successfully running on port ${port}`));
});
