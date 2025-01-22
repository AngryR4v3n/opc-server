# Dummy OPC Server
This is a docker image that serves to quickly initialize an OPC server that generates (fake) data. The OPC server will have the structure based on an input json file.

An example JSON file is included in order to demonstrate how it can dynamically upon initialization create tags based on the structure of the json.

# Building and running the Docker Image
1. Download/clone the repository
2. Open in terminal the folder where you cloned/downloaded the repository, run: `` sudo docker build -t <replace_me_with_image_name> .``
3. Run the image: ``sudo docker run -e OPC_STRUCTURE=<path_to_json_structure> -e TAG_FREQUENCY=<frequency_of_signals_in_seconds>``

## Creating your own JSON structure
In order to specify your own structure according to your needs you need to match the following schema: 

```
{
    "sitesMap": [
        {
            "site": "name_of_your_site"
            "assets": {
                "asset1": ["tag1", "tag2", "tag3"]
            }

        }

    ]
        
}
```

Any key that gets defined inside the "assets" that is of type **dictionary will be initialized in OPC UA server as a folder node**
If you wish to create tags, you need to define a key with its value as **an array**. All elements inside the array will be OPC tags that are children to it's key in the JSON.

The example shown below would create the following OPC UA structure:
```
SmartCompany/
├─ name_of_your_site/
│  ├─ asset1/
│  │  ├─ tag1
│  │  ├─ tag2
│  │  ├─ tag3
```