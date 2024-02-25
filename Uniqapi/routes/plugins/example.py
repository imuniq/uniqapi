from Uniqapi import app


@app.create_route(name="params",
                  tags=["basic"],
                  info="returns param value",
                  params=[
                      {
                        "name": "hello",
                       "required": True,
                        "info": "The value of World"
                      }],
                  anti_spam=4
                  )
def test_plugin_with_params():

    params, err = app._set_params(params=["hello"])
    if err:
        return app._jsonify(error=err), 400

    # rest of your codes
    return app._jsonify(message="example plugin route  with params...", hello=params.hello)


@app.route('/images/<path:image_path>')
def stream_image(image_path):
    image_url = f"https://i.imgur.com/EpHgJmX.gif"
    r = app.http_request.get(image_url, stream=True)

    # Check if the request was successful
    if r.status_code == 200:

        # Set the content type as image/jpeg
        headers = {'Content-Type': 'image/jpeg'}
        # Stream the image content as a response
        return app._set_response(r.content, headers=headers)

    else:
        return "Image not found", 404
