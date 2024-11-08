Observations:

- ~37,000: prompt tokens when matplotlib image is saved as base64 and included in prompt -TOO MANY
- Image URL method MUST be tried out to optimize token usage


- Image URL and base 64 both result in ~36,000 tokens if image quality is auto
- get similar results if image quality used in prompt message is kept 'low'
    - tokens used: only ~3000


IDEA
- what if image generation request is sent to both o1-mini and claude-3.5-sonnet
- next get both images QAd
- send [o1-mini-image, o1-mini-image-critique] to claude along with its own previously generated image and critique
- do the same for claude....let both LLMs act as adverseries and collaborators both...let both learn from each others diagrams
- finally let an arbitrer choose which diagram is the best