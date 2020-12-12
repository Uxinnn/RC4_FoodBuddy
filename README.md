RC4_FoodBuddy
===============
*Fight isolation with food!*

        ______________________________  ______  ___   __________  __________    ___
       /  _____/ __   /  __   /  __   \/  __  \/  /  /  /  __   \/  __   \  \  /  /
      /  __/ /  / /  /  / /  /  / /   /  /_/  /  /  /  /  / /   /  / /   /\  \/  /
     /  /   /  /_/  /  /_/  /  /_/   /  /__\  \  \_/  /  /_/   /  /_/   /  \    /
    /__/    \______/\______/\_______/_________/\_____/ \______/ \______/   /___/
 
 Work distribution:
 * Frontend Input: Alvin
 * Frontend Output: Xin Yu
 * Backend: Bryan, Mukund
 
To clone repo:
`git clone https://github.com/Uxinnn/RC4_FoodBuddy.git`

Git Workflow:
* `main` and `dev` are permanent branches. New branches should be created for new features.
* **Github**: Create new branch to work on
  * `<code><ID>_<task>`
    * Channel: CH
    * Bot: BT
    * Processor: PC
  * Eg. CH00_create_channel
*  **Local**: `git pull`
* **Local**: `git checkout <branch>`
* **Local**: Ensure correct branch is selected using `git branch`
* **Local**: Code
* **Local**: `git add <new files/directories`
* **Local**: `git commit -m "<message>"`
* **Local**: `git push origin <branch>`
* **Local**: Submit pull request
* **Local**: Pull request to be merged into `dev` branch after vetting
* **Local**: Delete local branch using `git branch -d <branch>`
* **Local**: Remove tracking of deleted remote branch using `git remote prune origin`
`dev` will be merged periodically into `main` for new version releases.