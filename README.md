# lemonbot

## What is it?

Lemonbot is a basic Facebook chatbot that provides game time and team information with data scraped from a sporting facility's website. Essentially, you send it a team name (or partial team name), it will find teams matching that name and then provide you the option to get the next game time for that team, or the current team performance/statistics.

## How do I use it?

1. Browse to the [LemonBot page](https://www.facebook.com/LemonBot-1763943487196046/) and click 'Message', or use [this link](http://m.me/1763943487196046) to open a conversation directly
2. Send a message! It'll tell you what to do. If that's a bit daunting, the screenshot below covers all the functionality

<img src="https://raw.githubusercontent.com/iJebus/lemonbot/gh-pages/images/demo.png" alt="example of lemonbot usage" style="width: 800px;"/>

P.S., it wasn't very nice of me to make it say dumb robot, was it. :(

## Why make it?

1. I had wanted an excuse to play with Zappa and this was a suitable use case
2. I play netball at this venue and want to make something more convenient for myself than checking their website
3. I needed a project for a university unit relating to cloud computing (CITS5503) that demonstrates a practical application of AWS Lambda

## What does it use?

Primarily...

* [Facebook Messenger Platform](https://developers.facebook.com/docs/messenger-platform) - For the chatting...
* [Requests](http://docs.python-requests.org/en/master) - for handling the web-scraping...
* [Zappa](https://github.com/Miserlou/Zappa) - for the bot...ing?

### Functional requirements

* Respond to messages
* Respond to requests for information about a team's current standing and stats
* Respond to requests for information about the time and date of a team's next game
* Scrape relevant team information from the sporting facility's website
* Provide a humanized version of the date/time in addition to a calender version, e.g., 'in 5 days', if the game is five days away

### Non-functional requirements

* Cheap to run, i.e., only billed when being accessed
* Easy to extend
* Easy to use
* Respond quickly (i.e., within a few seconds)
* Runs on Facebook
* Scales horizontally under load

## How could it be improved?

* Cache scraped results to prevent spamming of the original source with scrape requests. This is pretty important if this were project actually to be used, as currently under load it would just shift the pressure onto the sporting facility's backend, making the power of AWS Lambda to scale horizontally pretty moot. DynamoDB is a potential candidate for storing retrieved data
* Handling of time zones! Currently AWST is locked in
* Send messages regarding game time on a schedule, e.g., the day before the game
* Store 'favourites' or at least associate a team/teams with a user so that users don't need to request by teams name each time. DynamoDB again could be used to store team/player associations

## How can I run this code/build this project?

1. Firstly, I'd recommend running through Hartley Brody's tutorial, which incidently is linked below under the Resources heading. This will help you create a Facebook Page/App and get that configured for messaging.
2. Get Zappa installed; that's also linked below. Note that I'm using v0.27.1 and your mileage may vary with newer releases.
3. Create an AWS account and IAM user and all of that. Zappa documentation has details on those and what permissions it needs specifically, so read that. You'll need to create an S3 bucket, but that's covered too.
4. Okay now we're finally getting somewhere. After cloning this project, you'll need to create `zappa_settings.json` and populate it with values appropriate to your project. If you have followed Brody's tutorial and read the Zappa documentation, this won't be difficult. There's an example below.
5. You're ready to deploy! Run `zappa deploy dev` or whatever is appropriate to your `zappa_settings.json` configuration.
6. Provide your Facebook App with the appropriate callback URL that Zappa will have just provided you when it finished running. It will look something like this: `https://3oaw0urnj3.execute-api.us-east-1.amazonaws.com/dev/webhook`
7. Things should actually be working now. Try sending a message to your bot. If it doesn't work, something has gone horribly wrong. You can check the Zappa logs with `zappa tail dev`. 

*Example `zappa_settings.json` file*
```json
{
    "dev": {
        "app_function": "app.app",
        "s3_bucket": "lemon-bot",
	    "environment_variables": {
                "PAGE_ACCESS_TOKEN": "I'll be back.",
	        "VERIFY_TOKEN": "DYLAN! YOU SON OF A !"
            },
        "keep_warm": true
    }
}
```

*Example `zappa deploy dev` output*
```bash
$ zappa deploy dev
Important! A new version of Zappa is available!
Upgrade with: pip install zappa --upgrade
Visit the project page on GitHub to see the latest changes: https://github.com/Miserlou/Zappa
Packaging project as zip...
Uploading lemonbot-dev-1477837713.zip (10.5MiB)...
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 11.0M/11.0M [01:52<00:00, 103KB/s]
Updating Lambda function code..
Updating Lambda function configuration..
Uploading lemonbot-dev-template-1477837841.json (1.5KiB)...
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1.57K/1.57K [00:01<00:00, 873B/s]
Deploying API Gateway..
Scheduling..
Unscheduled lemonbot-dev-zappa-keep-warm-handler.keep_warm_callback.
Scheduled lemonbot-dev-zappa-keep-warm-handler.keep_warm_callback!
Your updated Zappa deployment is live!: https://3oaw0urnj3.execute-api.us-east-1.amazonaws.com/dev
```

## Resources

While I looked at a few guides and tutorials, there were three resources used primarily.

* Facebook's very own [documentation](https://developers.facebook.com/docs/messenger-platform) on the Messenger Platform
* Hartley Brody's [blog post](https://blog.hartleybrody.com/fb-messenger-bot/)  on using Python / Flask to create a chatbot, and the accompanying [github](https://github.com/hartleybrody/fb-messenger-bot) repository
* The Zappa project's [documentation](https://github.com/Miserlou/Zappa)

Brody's blog post is a great place to get started with the very basics, and will get you to the point of having a bot that will give a generic response to any messages. This project extends on that by...

* Implementing a rudimentary message router. This is part of a general aim to create smaller, more specific functions
* Templates for different types of responses / messages available in Facebook (e.g., simple text message, or a message with buttons?)
* All the website scraping and parsing stuff
* Handling of message seen, typing on/off indicators
* Postback message handling

## Fun Facebook caveats

* No more than three buttons in an message/element
* No more than ten 'bubbles' or elements per message
* It looks like Facebook retries failed messages when you have broken code. That's good except that it can make your logs hard to follow sometimes.
