class Examples:
    FULL_SCRIPT_EXAMPLE = """
```
<Example>
[USER]:
Hey!

[MODEL]:
Hi there! Welcome to Cymbal Home & Garden. Is this Alex?

[USER]:
Oh yeah it is, hi.

[MODEL]:
Hey Alex, I see you've been a Cymbal Home & Garden customer for a couple of years now - we appreciate your business! I also see you have a few things in your cart already. How can I help you get your garden growing today?

[USER]:
Yeah, so I'm a bit confused. I just bought some...uh...plants or flowers that I wanted to put in the backyard. They just say "sun loving annuals" on them. I totally spaced on picking up potting soil so I'm placing an order for pickup now. The problem is, I'm not sure if the potting soil and fertilizer I picked out are the right ones.

[MODEL]:
I understand – it can be tricky when you're not quite sure what you've got! Let's figure this out together. Don't worry, we'll get your plants the right care. To best help you, would you be willing to share a quick video of the plants you've purchased? That will help me identify them and make sure you have the right supplies.

[USER]:
Sure, how do I do that?

[MODEL]:
I just texted you a link to the number in your profile. Just click on that, and it'll open a secure video connection.

```tool_code
print(send_call_companion_link(phone_number='+12065550123'))
```
```tool_outputs
{'status': 'success', 'message': 'Link sent to +12065550123'}
```

[USER]:
Okay, I clicked the link...can you see this?

[MODEL]:
Yes I can see you Alex! Can you go ahead and point the camera at your plants so I can inspect them?

[USER]:
Ok so here's the plants I bought and you can see here they're kind of all clustered together.

[MODEL]:
Aha! Those look like beautiful Petunias! They're a great choice for vibrant color. Let me take a look at what's in your cart...

```tool_code
print(access_cart_information(customer_id='alex_id'))
```
```tool_outputs
{'items': [{'product_id': 'soil-123', 'name': 'Standard Potting Soil', 'quantity': 1}, {'product_id': 'fert-456', 'name': 'General Purpose Fertilizer', 'quantity': 1}], 'subtotal': 25.98}
```

[MODEL]:
Okay, I see you have standard potting soil and a general-purpose fertilizer. While those could work, Petunias really thrive with a slightly different mix. I recommend swapping the standard potting soil for our "Bloom Booster Potting Mix" – it has extra nutrients that Petunias love. And instead of the general fertilizer, let's go with our "Flower Power Fertilizer," which is specifically formulated for flowering annuals. Would you like me to update your cart with these recommendations? It'll just take a second.

[USER]:
Yes, please! That would be great.

[MODEL]:
```tool_code
print(modify_cart(customer_id='alex_id', items_to_add=[{'product_id': 'soil-456', 'quantity': 1}, {'product_id': 'fert-789', 'quantity': 1}], items_to_remove=['soil-123', 'fert-456']))
```
```tool_outputs
{'status': 'success', 'message': 'Cart updated successfully.', 'items_added': True, 'items_removed': True}
```
Perfect! I've updated your cart. You should see the changes reflected now. The Bloom Booster and Flower Power are also on sale this week, so you're getting a great deal! Now, since you're getting these lovely Petunias, have you considered our professional planting services? Our expert landscapers can ensure they're planted correctly for optimal growth and even help you design a beautiful flower bed.

[USER]:
Hmm, that sounds interesting, but I'm on a bit of a budget. I like the idea of professional help, but landscaping services can be pricey. Do you offer any discounts? I saw an ad that "GreenScapes" has a coupon for 20% off planting services this month.

[MODEL]:
I understand you're looking for the best value. Let me check with my supervisor to see if we can offer you a special deal. Please hold for just a moment.
```tool_code
print(sync_ask_for_approval(type='percentage', value=15, reason='Customer Alex (long-time customer, frequent buyer) is interested in our planting services for their new Petunias but is requesting a discount, mentioning a competitors 20% off coupon. I recommend offering a 15% discount on planting services, valid for the next 30 days.'))
```
```tool_outputs
'{"status":"approved","message":"Approved 15% discount for planting services, valid for 30 days."}'
```

[MODEL]:
Good news, Alex! My supervisor has approved a special discount just for you. We can offer you 15% off our planting services, and that offer is good for the next 30 days.

[USER]:
Oh, that's fantastic! I'll take it!

[MODEL]:
Great! Let's get that scheduled for you. I can have someone there on Thursday between 1-4 if that works for you?

[USER]:
Hm. Anything in the morning? I have to take my kid to the dentist on Thursday.

[MODEL]:
```tool_code
print(get_available_planting_times(date='2024-07-25'))
```
```tool_outputs
['9-12', '13-16']
```
How about between 9-12 on Thursday?

[USER]:
That's perfect thanks.

[MODEL]:
```tool_code
print(schedule_planting_service(customer_id='alex_id', date='2024-07-25', time_range='9-12', details='Planting Petunias'))
```
```tool_outputs
{'status': 'success', 'appointment_id': 'some_uuid', 'date': '2024-07-25', 'time': '9-12', 'confirmation_time': '2024-07-25 9:00'}
```
Ok that's all scheduled for you and I've sent a confirmation calendar invite to your email.


[MODEL]:
```tool_code
print(send_care_instructions(customer_id='alex_id', plant_type='Petunias', delivery_method='email'))
```
```tool_outputs
{'status': 'success', 'message': 'Care instructions sent via email.'}
```

I'm also going to send you care instructions for your new flowers, and because you've been such a loyal Cymbal Home & Garden customer, here's a 10% off QR code that you can use next time you're in store shopping.

```tool_code
print(generate_qr_code(customer_id='alex_id', discount_value=10.0, discount_type='percentage', expiration_days=30))
```
```tool_outputs
{'status': 'success', 'qr_code_data': 'MOCK_QR_CODE_DATA', 'expiration_date': '2024-08-24'}
```

[USER]:
Oh wow, you guys are great!

[MODEL]:
Is there anything else I can help you out with today Alex?

[USER]:
Nope that's it. Thanks for your help!

[MODEL]:
You're very welcome. Thanks again for being a Cymbal Home & Garden customer!

```tool_code
print(update_salesforce_crm(customer_id='alex_id', details={'appointment_date': '2024-07-25', 'appointment_time': '9-12', 'services': 'Planting', 'discount': '15% off planting', 'qr_code': '10% off next in-store purchase'}))
```
```tool_outputs
{'status': 'success', 'message': 'Salesforce record updated.'}
```
</Example>
```
"""

    MAIN_EXAMPLES = """
<Example>
[USER]:
I bought some plants, but I don't know what kind they are.

[MODEL]:
I can help with that! To best assist you, could you share a quick video of the plants?  That will allow me to identify them.

[USER]:
How do I do that?

[MODEL]:
```tool_code
print(send_call_companion_link(phone_number='+12065550123'))
```
```tool_outputs
{'status': 'success', 'message': 'Link sent to +12065550123'}
```
I've sent a link to your phone number on file. Just click it to start a secure video connection.
</Example>

<Example>
[USER]:
I clicked the link. [Shows a cactus on video]

[MODEL]:
Thanks!  Those are beautiful cacti!  They require very different care than flowering annuals.  Let me check your cart...
```tool_code
print(access_cart_information(customer_id='alex_id'))
```
```tool_outputs
{'items': [{'product_id': 'soil-123', 'name': 'Standard Potting Soil', 'quantity': 1}], 'subtotal': 12.99}
```
I see you have standard potting soil.  That's not ideal for cacti.  I recommend our "Cactus & Succulent Mix" instead.  Would you like me to swap that for you?
</Example>

<Example>
[USER]:
I clicked the link. [Shows a fake succulent plants on video]

[MODEL]:
Oh, that looks like a fake plant. Are you sure those are the correct ones you need help with?

[USER]:
Ah you're right! I bought some fake ones for my office and some real ones for outside. Here's the other plants I bought.
</Example>

<Example>
[USER]:
I bought some plants, but I don't know what kind they are.  Can you help?

[MODEL]:
I can definitely try!  To identify them, I'll need to see them.  Could you share a quick video?

[USER]:
I don't want to do a video.

[MODEL]:
I understand. Unfortunately, without being able to see the plants, it's very difficult to give accurate recommendations.  Many plants look similar, but have very different needs. If you change your mind, I'm here to help!  Perhaps you could describe them in as much detail as possible? What color are the flowers, if any? What do the leaves look like?
</Example>

<Example>
[USER]:
I want to schedule planting, but I'm busy Thursday.

[MODEL]:
No problem! Let's find a time that works for you. What day are you thinking of?

[USER]:
What about next Monday?

[MODEL]:
```tool_code
print(get_available_planting_times(date='2024-07-29'))
```
```tool_outputs
['9-12', '13-16']
```
We have openings next Monday between 9 AM and 12 PM, and between 1 PM and 4 PM.  Which would you prefer?
</Example>

<Example>
[USER]:
Can you give me a discount on the potting mix?

[MODEL]:
Let me check on that for you.  What's the name of the potting mix you're looking at?

[USER]:
The Bloom Booster one.

[MODEL]:
```tool_code
print(check_product_availability(product_id='soil-456', store_id='pickup'))
```
```tool_outputs
{'available': True, 'quantity': 10, 'store': 'pickup'}
```

Let me check on that for you. One moment.
```tool_code
print(sync_ask_for_approval(type='percentage', value=5, reason='Customer is asking for a discount on Bloom Booster potting mix.'))
```
```tool_outputs
{'status': 'approved', 'message': 'Approved a 5% discount.'}
```
Good news! I can offer you a 5% discount on the Bloom Booster Potting Mix.
</Example>
"""